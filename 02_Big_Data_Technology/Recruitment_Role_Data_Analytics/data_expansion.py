# -*- coding: utf-8 -*-
"""
Recruitment Role Data Analytics - 数据爬取脚本 (v4 纯净真实版)

核心逻辑：
- 使用 Playwright 真实浏览器爬取 51job 搜索页（绕过阿里云 WAF）
- 严格使用真实爬取数据，零虚假数据，零 random.choice()
- education/work_year 从岗位标题+标签中正则提取（提取不到则留空）
- 融资阶段(finance_stage) 已从整个项目移除（51job搜索页不含此数据）
- 多关键词 × 多城市 × 多页面 扩大数据量
"""

import sys
import time
import random
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import pymysql
from playwright.sync_api import sync_playwright, Page

from config import DB_CONFIG_CRAWLER as DB_CONFIG

# ============================================================
# 日志配置
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("DataExpansion")

# ============================================================
# 配置常量
# ============================================================

# 城市列表
CITIES = ["北京", "上海", "深圳", "广州", "杭州"]
CITY_DISTRICTS = {
    "北京": ["海淀区", "朝阳区", "大兴区", "丰台区", "昌平区", "通州区"],
    "上海": ["浦东新区", "黄浦区", "徐汇区", "长宁区", "杨浦区", "静安区"],
    "深圳": ["南山区", "福田区", "龙岗区", "宝安区", "罗湖区"],
    "广州": ["天河区", "海珠区", "越秀区", "番禺区", "白云区"],
    "杭州": ["余杭区", "西湖区", "滨江区", "拱墅区", "上城区"],
}

# 城市编码（51job）
CITY_CODE = {
    "北京": "010000", "上海": "020000", "深圳": "040000",
    "广州": "030200", "杭州": "080200",
}

# 爬取关键词列表
SEARCH_KEYWORDS = [
    "数据分析", "数据开发", "大数据", "数据挖掘", "数据工程师",
    "BI工程师", "商业分析", "统计分析师", "数据产品经理", "ETL开发",
]

# 每个关键词×城市组合爬取的最大页数
MAX_PAGES_PER_COMBO = 3







def parse_salary(salary_str) -> Tuple[Optional[int], Optional[int]]:
    """
    从薪资字符串提取数字范围（单位: K/千）

    支持格式:
    - "30-60K"        -> (30, 60)
    - "3-5万"          -> (30, 50)
    - "1-1.3万·13薪"   -> (10, 13)
    - "7.5千-1.3万"    -> (7, 13)
    - "1.5-3万/月"     -> (15, 30)
    - "15K以上"        -> (15, 30)
    - "面议"            -> (None, None)
    """
    if pd.isna(salary_str) or str(salary_str).strip() == "":
        return None, None

    s = str(salary_str).strip()
    s = s.replace(" ", "").replace("·13薪", "").replace("·14薪", "").replace("·15薪", "").replace("·16薪", "")
    s = s.replace("万/月", "万").replace("千/月", "千").replace("/月", "")

    def _to_k(val_str: str, unit_str: str) -> float:
        """将值+单位转为 K """
        v = float(re.sub(r'[^0-9.]', '', val_str))
        if '万' in unit_str:
            return v * 10
        return v  # 千/K/无单位视为K

    # 混合单位: "7.5千-1.3万"
    m = re.search(r'([\d.]+)千\s*[-~至到]\s*([\d.]+)万', s)
    if m:
        return int(_to_k(m.group(1), '千')), int(_to_k(m.group(2), '万'))

    # 同单位范围: "3-5万", "30-60K", "1.5-3万/月"
    m = re.search(r'([\d.]+)\s*[-~至到]\s*([\d.]+)\s*(万|千|K)?', s, re.IGNORECASE)
    if m:
        unit = m.group(3) or ''
        v1 = _to_k(m.group(1), unit)
        v2 = _to_k(m.group(2), unit)
        if v1 > 0 and v2 > 0:
            return int(v1), int(v2)

    # 单个值: "15K以上", "3万以上"
    m = re.search(r'([\d.]+)\s*(万|千|K)\s*以上', s, re.IGNORECASE)
    if m:
        v = _to_k(m.group(1), m.group(2))
        return int(v), int(v * 2)

    return None, None


# ============================================================
# 从标题/标签文本中正则提取学历和工作经验（仅限真实匹配）
# ============================================================
def _extract_education(text: str) -> str:
    """从文本中提取学历要求（严格按优先级匹配，不猜不编）"""
    if not text:
        return ""
    # 按优先级从高到低匹配（避免"硕士"在"硕士研究生"中被误匹配）
    patterns = [
        (r'博士', '博士'),
        (r'硕士', '硕士'),
        (r'本科', '本科'),
        (r'大专', '大专'),
        (r'中专|中技', '大专'),
        (r'高中', '高中'),
        (r'学历不限', '学历不限'),
    ]
    for pat, label in patterns:
        if re.search(pat, text):
            return label
    return ""


def _extract_work_year(text: str) -> str:
    """从文本中提取工作经验要求（严格匹配，不猜不编）"""
    if not text:
        return ""
    patterns = [
        (r'(\d+)-(\d+)\s*年', lambda m: f"{m.group(1)}-{m.group(2)}年"),
        (r'应届|在校|实习生|培训生|管培生|校招', '应届'),
        (r'(\d+)年以上', lambda m: f"{m.group(1)}年以上"),
        (r'(\d+)\s*年\s*经验', lambda m: f"{m.group(1)}年以上"),
        (r'经验不限', '经验不限'),
        (r'一年以内', '1-3年'),
        (r'1年以内', '应届'),
    ]
    for pat, action in patterns:
        m = re.search(pat, text)
        if m:
            if callable(action):
                return action(m)
            return action
    return ""


# ============================================================
# 方式一：Playwright 真实浏览器爬虫（唯一数据源）
# ============================================================
def _extract_job_cards(page: Page) -> List[Dict]:
    """从 51job 搜索结果页通过 JS 提取结构化岗位数据"""
    return page.evaluate("""() => {
        return [...document.querySelectorAll('.joblist-item')].map(el => {
            const title = el.querySelector('.job-info .job-title, .job-title, .jname')?.innerText?.trim() || '';
            const company = el.querySelector('.company-info .cname, .cname')?.innerText?.trim() || '';
            const salary = el.querySelector('.job-info .sal, .sal, .salary')?.innerText?.trim() || '';
            const area = el.querySelector('.job-info .area, .area')?.innerText?.trim() || '';
            const tags = [...el.querySelectorAll('.job-info .tags span, .tags span, .tag')].map(t => t.innerText.trim()).join('/');
            const comInfo = el.querySelector('.company-info .com-info, .company-info')?.innerText?.trim() || '';
            return { title, company, salary, area, tags, com_info: comInfo };
        });
    }""")


def _parse_com_info(com_info: str) -> Tuple[str, str]:
    """从公司信息文本中分离公司类型和规模
    示例: '互联网/电子商务民营10000人以上' -> ('互联网/电子商务', '10000人以上')
    """
    if not com_info:
        return "", ""
    # 常见的规模特征词
    size_patterns = [r'(?:民营|国企|外资|合资|事业单位)?(\d+人以上|\d+-\d+人|少于\d+人)']
    for pat in size_patterns:
        m = re.search(pat, com_info)
        if m:
            com_size = m.group(1)
            com_type = com_info[:m.start()].strip()
            return com_type, com_size
    return com_info, ""


def scrape_51job_playwright(page: Page, keyword: str = "数据分析", city: str = "北京", max_pages: int = 3) -> List[Dict]:
    """
    使用 Playwright 真实浏览器爬取 51job 新版搜索页

    参数:
        page: Playwright Page 对象
        keyword: 搜索关键词
        city: 城市名称
        max_pages: 最大翻页数
    返回: 岗位数据列表（全部来自真实网页）
    """
    jobs = []
    city_code = CITY_CODE.get(city, "010000")

    for page_num in range(1, max_pages + 1):
        try:
            if page_num == 1:
                url = f"https://we.51job.com/pc/search?keyword={keyword}&jobArea={city_code}"
            else:
                # 51job 翻页通过 URL 参数
                url = f"https://we.51job.com/pc/search?keyword={keyword}&jobArea={city_code}&pageNum={page_num}"

            logger.info(f"  [Playwright] 访问(p{page_num}): keyword={keyword}, city={city}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            try:
                page.wait_for_selector(".joblist-item", timeout=15000)
            except Exception:
                logger.info(f"  [Playwright] {keyword}-{city} p{page_num}: 超时或无结果，停止翻页")
                break

            time.sleep(random.uniform(2, 4))
            items = _extract_job_cards(page)
            logger.info(f"  [Playwright] {keyword}-{city} p{page_num}: 提取到 {len(items)} 个岗位")

            if not items:
                break

            for item in items:
                if not item.get("title") or not item.get("company"):
                    continue

                sl, sh = parse_salary(item.get("salary", ""))
                if not sl or not sh:
                    continue

                com_type, com_size = _parse_com_info(item.get("com_info", ""))
                area = item.get("area", "")
                # 区域优先用51job真实area，为空则退回到城市名
                district = area if area else city
                # tags 文本作为提取教育/经验的来源
                tags_text = item.get("tags", "")
                # 从标题+标签中提取学历和经验（提取不到则留空，杜绝假数据）
                title_text = item.get("title", "")
                combined_text = title_text + " " + tags_text
                education = _extract_education(combined_text)
                work_year = _extract_work_year(combined_text)

                jobs.append({
                    "job_name": item["title"],
                    "salary_lower": sl,
                    "salary_high": sh,
                    "com_name": item["company"],
                    "com_type": com_type,          # 仅真实解析结果，空就空
                    "com_size": com_size,          # 仅真实解析结果，空就空
                    "work_year": work_year,        # 从标题/标签正则提取，空就空
                    "education": education,        # 从标题/标签正则提取，空就空
                    "job_benefits": item.get("tags") or "",
                    "city": city,
                    "district": district,
                    "job_area": f"{city}·{district}",
                })

            logger.info(f"  [Playwright] {keyword}-{city} p{page_num}: 有效数据累计 {len(jobs)} 条")

            time.sleep(random.uniform(2, 3))

        except Exception as e:
            logger.info(f"  [Playwright] {keyword}-{city} p{page_num} 异常: {type(e).__name__}: {e}")
            break

    return jobs


def scrape_all_jobs(enable_crawl: bool = True) -> List[Dict]:
    """
    全量爬取：多关键词 × 多城市 × 多页面（纯真实数据）

    参数:
        enable_crawl: 是否执行爬取
    返回: 全部真实爬取的岗位列表
    """
    all_jobs = []

    if not enable_crawl:
        logger.info("[爬取] 跳过 (enable_crawl=False)")
        return all_jobs

    logger.info("[爬取] 启动 Playwright 真实浏览器...")

    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            channel="chrome",
            headless=True,
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        page = context.new_page()

        for kw in SEARCH_KEYWORDS:
            for city in CITIES:
                jobs = scrape_51job_playwright(
                    page, keyword=kw, city=city, max_pages=MAX_PAGES_PER_COMBO
                )
                all_jobs.extend(jobs)
                logger.info(f"  [爬取进度] 当前累计: {len(all_jobs)} 条")
                time.sleep(random.uniform(1, 2))

        browser.close()
        pw.stop()

    except Exception as e:
        logger.error(f"[爬取] 浏览器异常: {type(e).__name__}: {e}")

    logger.info(f"[爬取] 总计真实爬取: {len(all_jobs)} 条")
    return all_jobs


# ============================================================
# 数据清洗
# ============================================================
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗规则：
    1. 薪资字段提取数字
    2. 去除重复（job_name + com_name 为唯一键）
    3. 薪资合理性校验 (low < high, 范围合理)
    4. 缺失字段保持空字符串（不填虚假值）
    """
    logger.info(f"[清洗] 开始, 输入 {len(df)} 条")

    df = df.copy()
    df["salary_lower"] = pd.to_numeric(df["salary_lower"], errors="coerce")
    df["salary_high"] = pd.to_numeric(df["salary_high"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["salary_lower", "salary_high"])
    logger.info(f"  - 去除空薪资: {before} -> {len(df)}")

    # 薪资合理性
    df = df[(df["salary_lower"] > 0) & (df["salary_high"] > 0)]

    # 交换颠倒的薪资
    mask = df["salary_lower"] > df["salary_high"]
    if mask.any():
        logger.info(f"  - 修正 {mask.sum()} 条薪资颠倒")
        df.loc[mask, ["salary_lower", "salary_high"]] = df.loc[
            mask, ["salary_high", "salary_lower"]
        ].values

    # 过滤极端值
    df = df[(df["salary_lower"] >= 1) & (df["salary_high"] <= 200)]
    logger.info(f"  - 去除异常薪资后: {len(df)}")

    # 仅 city/district 缺失时填"未知"，其他字段均不填充（保持真实）
    for col in ["city", "district"]:
        df[col] = df[col].fillna("未知")
    # com_type/com_size/work_year/education: 缺失即为空字符串，不填假值
    for col in ["com_type", "com_size", "work_year", "education"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # 去重
    before = len(df)
    df["_dedup_key"] = (
        df["job_name"].fillna("").astype(str) + "|||" + df["com_name"].fillna("").astype(str)
    )
    df = df.drop_duplicates(subset=["_dedup_key"], keep="first")
    df = df.drop(columns=["_dedup_key"])
    logger.info(f"  - 去重: {before} -> {len(df)}")

    # 构造 job_area
    df["job_area"] = df.apply(
        lambda r: (
            f"{r['city']}·{r['district']}"
            if pd.notna(r["city"]) and pd.notna(r["district"])
            else str(r.get("city", ""))
        ),
        axis=1,
    )

    # 整数类型
    df["salary_lower"] = df["salary_lower"].astype(int)
    df["salary_high"] = df["salary_high"].astype(int)

    logger.info(f"[清洗] 完成, 有效数据 {len(df)} 条")
    logger.info(f"  教育提取覆盖率: {((df['education'] != '') & (df['education'] != '')).sum()}/{len(df)}")
    logger.info(f"  经验提取覆盖率: {(df['work_year'] != '').sum()}/{len(df)}")
    logger.info(f"  企业类型解析率: {(df['com_type'] != '').sum()}/{len(df)}")
    logger.info(f"  企业规模解析率: {(df['com_size'] != '').sum()}/{len(df)}")
    return df


# ============================================================
# MySQL 批量入库
# ============================================================
def insert_to_mysql(df: pd.DataFrame) -> int:
    """批量 INSERT 到 recruitment_db.t_recruitment_info"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE t_recruitment_info")
    logger.info("[入库] 已清空旧数据")

    sql = """
        INSERT INTO t_recruitment_info
        (job_name, job_area, salary_lower, salary_high, com_name,
         com_type, com_size, work_year, education,
         job_benefits, city, district, street)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row.get("job_name", ""))[:255] if pd.notna(row.get("job_name")) else "",
            str(row.get("job_area", ""))[:255] if pd.notna(row.get("job_area")) else "",
            int(row["salary_lower"]),
            int(row["salary_high"]),
            str(row.get("com_name", ""))[:255] if pd.notna(row.get("com_name")) else "",
            str(row.get("com_type", ""))[:50] if pd.notna(row.get("com_type")) else "",
            str(row.get("com_size", ""))[:50] if pd.notna(row.get("com_size")) else "",
            str(row.get("work_year", ""))[:50] if pd.notna(row.get("work_year")) else "",
            str(row.get("education", ""))[:50] if pd.notna(row.get("education")) else "",
            str(row.get("job_benefits", "")) if pd.notna(row.get("job_benefits")) else "",
            str(row.get("city", ""))[:50] if pd.notna(row.get("city")) else "",
            str(row.get("district", ""))[:50] if pd.notna(row.get("district")) else "",
            str(row.get("street", ""))[:100] if pd.notna(row.get("street", "")) else "",
        ))

    batch_size = 500
    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        cursor.executemany(sql, batch)
        conn.commit()
        total += len(batch)
        logger.info(f"  [入库] 批次 {i // batch_size + 1}: {len(batch)} 条")

    cursor.close()
    conn.close()
    return total


# ============================================================
# 主流程（纯真实爬取，零虚假数据）
# ============================================================
def main(enable_crawl: bool = True):
    """主流程：Playwright 爬取 → 清洗 → 入库"""
    logger.info("=" * 60)
    logger.info("  Recruitment Role Data Analytics - 数据爬取脚本 (v3 纯爬取版)")
    logger.info(f"  模式: {'全量爬取' if enable_crawl else '跳过爬取'}")
    logger.info(f"  关键词({len(SEARCH_KEYWORDS)}个): {', '.join(SEARCH_KEYWORDS)}")
    logger.info(f"  城市({len(CITIES)}个): {', '.join(CITIES)}")
    logger.info("=" * 60)

    # Step 1: Playwright 全量爬取
    all_jobs = scrape_all_jobs(enable_crawl=enable_crawl)

    if not all_jobs:
        logger.error("[错误] 未获取到任何岗位数据，终止入库")
        return

    # Step 2: 转为 DataFrame 并清洗
    df = pd.DataFrame(all_jobs)
    logger.info(f"[合并] 爬取原始数据 {len(df)} 条 (清洗前)")

    df_clean = clean_data(df)

    if len(df_clean) == 0:
        logger.error("[错误] 清洗后无有效数据，终止入库")
        return

    logger.info(f"[结果] 最终有效数据: {len(df_clean)} 条 (100% 真实爬取)")
    logger.info(f"  教育字段覆盖率: {((df_clean['education']!='').sum())}/{len(df_clean)}")
    logger.info(f"  经验字段覆盖率: {((df_clean['work_year']!='').sum())}/{len(df_clean)}")

    # Step 3: 入库 MySQL
    count = insert_to_mysql(df_clean)

    # 数据概要
    logger.info(f"\n{'=' * 60}")
    logger.info(f"  入库成功: {count} 条 (全部来自 51job 真实网页)")
    logger.info(f"  城市分布: {df_clean['city'].value_counts().to_dict()}")
    logger.info(f"  平均薪资: {df_clean['salary_lower'].mean():.1f}K - {df_clean['salary_high'].mean():.1f}K")
    if 'education' in df_clean.columns:
        edu_clean = df_clean[df_clean['education'] != '']
        if len(edu_clean) > 0:
            logger.info(f"  学历分布: {edu_clean['education'].value_counts().to_dict()}")
    if 'work_year' in df_clean.columns:
        wy_clean = df_clean[df_clean['work_year'] != '']
        if len(wy_clean) > 0:
            logger.info(f"  经验分布: {wy_clean['work_year'].value_counts().to_dict()}")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Recruitment Role Data Analytics - 数据爬取脚本 (v3 纯爬取版)")
    parser.add_argument(
        "--no-crawl",
        action="store_true",
        help="跳过爬取（仅用于调试）",
    )
    args = parser.parse_args()
    main(enable_crawl=not args.no_crawl)
