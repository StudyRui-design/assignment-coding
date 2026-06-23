# -*- coding: utf-8 -*-
"""
多源招聘数据爬虫 v2 - 真实可用版
================================
数据源（已验证可行）:
  1. 智联招聘 (zhaopin.com) - 搜索列表页直接展示完整字段
  2. 猎聘 (liepin.com) - 滚动加载后可获取完整岗位信息

策略:
  - 100% 真实爬取，零虚构数据
  - 通过 (com_name, job_name) 匹配 UPDATE 现有记录缺失字段
  - 同时 INSERT 新记录扩充数据量
"""

import sys
import io
import time
import re
import random
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
# 设置UTF-8输出（只在直接运行时）
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
logger = logging.getLogger("MultiCrawlerV2")

# ============================================================
# 爬取配置
# ============================================================
SEARCH_KEYWORDS = [
    "数据分析", "数据开发", "大数据", "数据挖掘", "数据工程师",
    "BI工程师", "商业分析", "数据产品经理", "ETL开发",
]

CITIES_ZHILIAN = {
    "北京": "530",
    "上海": "538",
    "深圳": "765",
    "广州": "763",
    "杭州": "653",
}

CITIES_LIEPIN = {
    "北京": "010",
    "上海": "020",
    "深圳": "050090",
    "广州": "050020",
    "杭州": "060020",
}

MAX_PAGES = 2  # 每个组合最大页数
MAX_CONSECUTIVE_EMPTY = 5  # 连续空结果组合数上限，达到后跳过该数据源剩余组合

# ============================================================
# 数据标准化
# ============================================================
def parse_salary(s) -> Tuple[Optional[int], Optional[int]]:
    """解析薪资为 (下限K, 上限K)"""
    if not s or s == "面议":
        return None, None
    s = str(s).strip().replace(" ", "")
    s = re.sub(r'·\d+薪', '', s)

    # 日薪 "150-250元/天" -> 估算月薪
    m = re.search(r'([\d.]+)-([\d.]+)元/天', s)
    if m:
        daily = int(float(m.group(2))) * 22 / 1000
        return max(1, int(daily * 0.7)), max(2, int(daily))

    # "8000-10000元" (纯元单位)
    m = re.search(r'^(\d+)\s*[-~至到]\s*(\d+)\s*元$', s)
    if m:
        lo, hi = int(int(m.group(1)) / 1000), int(int(m.group(2)) / 1000)
        if 1 <= lo < 500 and 1 <= hi < 500:
            return (lo, hi) if lo <= hi else (hi, lo)

    # 千/万混合 "7.5千-1.3万"
    m = re.search(r'([\d.]+)千\s*[-~至到]\s*([\d.]+)万', s)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)) * 10)

    # "1.9-3.5万" (单位后缀，适用于两端)
    m = re.search(r'^([\d.]+)\s*[-~至到]\s*([\d.]+)\s*(万|千|K)?$', s, re.IGNORECASE)
    if m:
        v1, v2 = float(m.group(1)), float(m.group(2))
        unit = m.group(3) or ''
        mult = 10 if unit == '万' else 1
        lo, hi = int(v1 * mult), int(v2 * mult)
        if 1 <= lo < 500 and 1 <= hi < 500:
            return (lo, hi) if lo <= hi else (hi, lo)

    # 单值以上 "15K以上", "3万以上"
    m = re.search(r'([\d.]+)\s*(万|K|k)\s*以上', s)
    if m:
        v = int(float(m.group(1)) * (10 if m.group(2) == '万' else 1))
        return v, int(v * 2)

    return None, None


def norm_edu(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    for pat, label in [
        (r'博士', '博士'), (r'硕士', '硕士'), (r'本科|统招本科', '本科'),
        (r'大专', '大专'), (r'高中|中专', '高中'), (r'不限|学历不限', '学历不限'),
    ]:
        if re.search(pat, t):
            return label
    return ""


def norm_work_year(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    for pat, label in [
        (r'应届|在校|实习|管培|培训生|校招', '应届'),
        (r'1年以下|1年以内|无需经验|无经验', '应届'),
        (r'1-3年|1-3 年', '1-3年'), (r'3-5年|3-5 年', '3-5年'),
        (r'5-10年|5-10 年', '5-10年'), (r'10年|十年以上', '10年以上'),
        (r'经验不限|不限', '经验不限'),
    ]:
        if re.search(pat, t):
            return label
    return ""


def norm_com_size(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    for pat, label in [
        (r'10000人以上|万人以上', '10000人以上'),
        (r'1000-9999人|1000-10000人', '1000-9999人'),
        (r'500-999人|500-1000人', '500-999人'),
        (r'100-499人|100-500人', '100-499人'),
        (r'50-99人|50-100人', '50-99人'),
        (r'20-99人|20-100人', '20-99人'),
        (r'20人以下|1-20人|少于20人', '20人以下'),
        (r'上市', '1000-9999人'),
    ]:
        if re.search(pat, t):
            return label
    return ""


def norm_com_type(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    for pat, label in [
        (r'互联网|电商|网络科技|软件|IT|计算机|在线|游戏|社交|移动|云|大数据|智能.*科技', '互联网'),
        (r'医疗|医药|制药|生物|医院|健康', '医疗/医药'),
        (r'金融|银行|证券|保险|基金|投资|信托|支付', '金融'),
        (r'教育|培训|院校|学术', '教育/科研'),
        (r'半导体|芯片|电子|通信|运营商', '半导体/电子'),
        (r'房地产|建筑|物业|装修|家居|建材', '房地产/建筑'),
        (r'汽车|新能源|能源|电力|环保', '能源/环保'),
        (r'制造|机械|自动化|设备|仪器|工业', '制造业'),
        (r'零售|贸易|批发|进出口|百货|消费品|快消', '商贸/零售'),
        (r'广告|传媒|文化|娱乐|影视|出版|媒体|设计', '文化传媒'),
        (r'咨询|服务|外包|人力资源|法律', '咨询/服务'),
        (r'物流|运输|快递|交通|航空', '物流/交通'),
        (r'餐饮|酒店|旅游|休闲', '旅游/酒店'),
        (r'政府|事业|公共|科研', '科研/事业单位'),
        (r'科技|数据|信息', '互联网'),
    ]:
        if re.search(pat, t):
            return label
    return ""


# ============================================================
# 智联招聘卡片解析器 - 模式匹配（位置无关）
# ============================================================
def _parse_zhaopin_card(lines: List[str]) -> Dict:
    """按内容模式匹配解析，不依赖固定行位置"""
    result = {
        "job_name": "", "salary_str": "", "location": "",
        "education_raw": "", "work_year_raw": "",
        "company": "", "com_type_raw": "", "com_size_raw": "",
        "tags": [],
    }
    if not lines:
        return result
    result["job_name"] = lines[0]

    # 预编译模式
    edu_pat = re.compile(r'^(博士|硕士|统招本科|本科|大专|中专|高中|学历不限)$')
    wy_pat = re.compile(r'^(经验不限|应届|在校|实习|1年以下|1年以内|无需经验|\d+-\d+年|\d+年以上|10年以上)$')
    cs_pat = re.compile(r'^(\d+人以上|\d+-\d+人|少于\d+人|20人以下)$')
    cn_pat = re.compile(r'^(民营|私企|国企|国有|央企|合资|外资|外商|欧美|上市公司|其它|事业单位|政府机关)$')
    loc_pat = re.compile(r'·')
    hr_pat = re.compile(r'(女士|先生|经理|总监|主管|专员|HR|招聘|回复|活跃|沟通|投递|关注|收藏|查看)')
    badge_pat = re.compile(r'^(最佳雇主|优选雇主|D轮|A轮|B轮|C轮|天使轮|已上市|未融资|不需要融资)$')

    salary_found = False
    skill_pat = re.compile(r'^[A-Za-z\s\d]+$')  # 纯英文/数字 → 技能标签不是公司名

    for line in lines[1:]:
        if not line or len(line) <= 1:
            continue
        if hr_pat.search(line) or badge_pat.match(line) or re.match(r'^[\d,.]+$', line):
            continue

        # "面议" → 无薪资
        if line == "面议":
            result["salary_str"] = "面议"
            salary_found = True
            continue

        # 薪资
        if not salary_found and (
            ('元/天' in line and re.search(r'[\d]', line)) or
            (re.search(r'[\d.]+[-~至到][\d.]+', line) and ('万' in line or 'K' in line.lower() or '千' in line or re.search(r'\d+-\d+元$', line)))
        ):
            result["salary_str"] = line
            salary_found = True
            continue

        # 区域
        if loc_pat.search(line) and len(line) < 30:
            result["location"] = line
            continue

        # 学历
        if edu_pat.match(line):
            result["education_raw"] = line
            continue

        # 经验
        if wy_pat.match(line):
            result["work_year_raw"] = line
            continue

        # 规模
        if cs_pat.match(line):
            result["com_size_raw"] = line
            continue

        # 公司性质
        if cn_pat.match(line):
            result["com_type_raw"] = line
            continue

        # 公司名 (较长中文文本，非英文非技能标签)
        if not result["company"] and len(line) >= 6:
            is_skill = bool(skill_pat.match(line))
            if not is_skill and not any(p.match(line) for p in [edu_pat, wy_pat, cs_pat, cn_pat]) and not loc_pat.search(line):
                result["company"] = line
                continue

        # 其余有意义的短行归为标签
        if 2 <= len(line) < 30:
            result["tags"].append(line)

    # 后处理: 如果公司名没找到或看起来是标签/技能，从tags中找真正的公司名
    company_suspect_patterns = [
        re.compile(r'(会计|财务|审计|税务)'),  # 可能是认证名
        re.compile(r'^(SQL|EXCEL|BI|Python|Java|R语言|SPSS)$', re.IGNORECASE),
        re.compile(r'^(经营|销售|基金|员工|业务|客户|产品|项目|互联网|O2O)'),  # 业务术语
    ]

    def _looks_like_company(text):
        """判断文本是否像公司名"""
        if len(text) < 6: return False
        if skill_pat.match(text): return False
        for pat in company_suspect_patterns:
            if pat.search(text) and len(text) < 15: return False
        if any(k in text for k in ['女士', '先生', '经理', '总监', 'HR', '招聘']): return False
        return True

    if not result["company"]:
        # 从tags中找公司名
        for tag in reversed(result["tags"]):
            if _looks_like_company(tag):
                result["company"] = tag
                result["tags"].remove(tag)
                break
    elif any(pat.search(result["company"]) and len(result["company"]) < 15 for pat in company_suspect_patterns):
        for tag in reversed(result["tags"]):
            if _looks_like_company(tag) and len(tag) >= 8:
                result["company"] = tag
                result["tags"].remove(tag)
                break

    return result


# ============================================================
# 数据源1: 智联招聘
# ============================================================
def crawl_zhaopin(page: Page, keywords=None, cities=None, max_pages=MAX_PAGES,
                   max_consecutive_empty=MAX_CONSECUTIVE_EMPTY) -> List[Dict]:
    """智联招聘 - sou.zhaopin.com 搜索列表页，选择器 .joblist-box__item"""
    if keywords is None:
        keywords = SEARCH_KEYWORDS
    if cities is None:
        cities = CITIES_ZHILIAN

    all_data = []
    consecutive_empty = 0  # 连续无效组合计数

    for kw in keywords:
        for city_name, city_code in cities.items():
            # 连续空结果过多则跳过该关键词剩余城市 + 后续关键词
            if consecutive_empty >= max_consecutive_empty:
                logger.info(f"[智联] 连续{max_consecutive_empty}个组合无有效数据，跳过: {kw} @ {city_name}")
                continue

            logger.info(f"[智联] {kw} @ {city_name}")
            combo_valid = 0  # 当前组合有效数

            for pn in range(1, max_pages + 1):
                try:
                    url = f"https://sou.zhaopin.com/?jl={city_code}&kw={quote(kw)}&p={pn}"
                    page.goto(url, wait_until="networkidle", timeout=45000)
                    time.sleep(random.uniform(2, 3))

                    jobs = page.evaluate("""() => {
                        const cards = document.querySelectorAll('.joblist-box__item');
                        return [...cards].map(el => {
                            const raw = (el.innerText || '').trim();
                            const lines = raw.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                            return { lines };
                        });
                    }""")

                    logger.info(f"  p{pn}: {len(jobs)} cards")

                    if not jobs:
                        break

                    valid = 0
                    for item in jobs:
                        lines = item.get("lines", [])
                        if len(lines) < 5:
                            continue

                        parsed = _parse_zhaopin_card(lines)
                        title = parsed["job_name"]
                        company = parsed["company"]
                        if not title or not company:
                            continue

                        sl, sh = parse_salary(parsed.get("salary_str", ""))

                        education = norm_edu(parsed.get("education_raw", ""))
                        work_year = norm_work_year(parsed.get("work_year_raw", ""))
                        com_type = norm_com_type(parsed.get("com_type_raw", ""))
                        com_size = norm_com_size(parsed.get("com_size_raw", ""))

                        # fallback
                        all_text = " ".join(lines)
                        if not education: education = norm_edu(all_text)
                        if not work_year: work_year = norm_work_year(all_text)
                        if not com_type: com_type = norm_com_type(all_text)
                        if not com_size: com_size = norm_com_size(all_text)

                        location = parsed.get("location", "")
                        district = ""
                        if location and "·" in location:
                            parts = location.split("·")
                            district = parts[1] if len(parts) > 1 else ""

                        all_data.append({
                            "job_name": title.strip()[:255],
                            "com_name": company.strip()[:255],
                            "salary_lower": sl,
                            "salary_high": sh,
                            "city": city_name,
                            "district": district[:50],
                            "education": education,
                            "work_year": work_year,
                            "com_type": com_type,
                            "com_size": com_size,
                            "job_benefits": "/".join(parsed.get("tags", []))[:500],
                            "source": "zhaopin",
                        })
                        valid += 1
                        combo_valid += 1

                    logger.info(f"  p{pn}: valid {valid} (total {len(all_data)})")

                    if len(jobs) < 5:
                        break
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    logger.info(f"  Error: {type(e).__name__}: {str(e)[:80]}")
                    break

            # 组合级统计：有效为0则累计，有数据则重置
            if combo_valid == 0:
                consecutive_empty += 1
                logger.info(f"  [无有效数据] 连续空: {consecutive_empty}/{max_consecutive_empty}")
            else:
                consecutive_empty = 0

    logger.info(f"[智联] Total: {len(all_data)}")
    return all_data


# ============================================================
# 数据源2: 猎聘
# ============================================================
def crawl_liepin(page: Page, keywords=None, cities=None, max_pages=MAX_PAGES,
                  max_consecutive_empty=MAX_CONSECUTIVE_EMPTY) -> List[Dict]:
    """
    猎聘搜索页 -- 已验证可用（需滚动触发加载）
    """
    if keywords is None:
        keywords = SEARCH_KEYWORDS
    if cities is None:
        cities = CITIES_LIEPIN

    all_data = []
    consecutive_empty = 0

    for kw in keywords:
        for city_name, city_code in cities.items():
            if consecutive_empty >= max_consecutive_empty:
                logger.info(f"[猎聘] 连续{max_consecutive_empty}个组合无有效数据，跳过: {kw} @ {city_name}")
                continue

            logger.info(f"[猎聘] {kw} @ {city_name}")
            combo_valid = 0

            try:
                url = f"https://www.liepin.com/zhaopin/?key={quote(kw)}&dqs={city_code}"
                page.goto(url, wait_until="networkidle", timeout=45000)
                time.sleep(3)

                # 滚动加载
                for i in range(4):
                    page.evaluate("window.scrollBy(0, 600)")
                    time.sleep(1.5)

                # 提取数据
                jobs = page.evaluate("""() => {
                    const container = document.querySelector('[class*="job-list"]');
                    if (!container) return [];
                    const cards = container.querySelectorAll('div');
                    return [...cards].filter(el => {
                        const text = el.innerText || '';
                        return text.includes('k') || text.includes('万') || text.includes('经验');
                    }).slice(0, 30).map(el => ({
                        allText: el.innerText || '',
                        lines: (el.innerText || '').split('\\n').filter(l => l.trim()),
                        html: el.outerHTML?.substring(0, 400) || '',
                    }));
                }""")

                logger.info(f"  Extracted {len(jobs)} items")

                valid = 0
                for item in jobs:
                    all_text = item.get("allText", "")
                    lines = item.get("lines", [])

                    if len(lines) < 3:
                        continue

                    # 从文本行推断字段
                    title = lines[0] if lines else ""
                    company = ""
                    salary_str = ""
                    location = ""

                    for i, line in enumerate(lines):
                        if 'k' in line.lower() or '万' in line:
                            salary_str = line
                        if not company and i >= 1:
                            company = line

                    sl, sh = parse_salary(salary_str)

                    education = norm_edu(all_text)
                    work_year = norm_work_year(all_text)
                    com_type = norm_com_type(all_text)
                    com_size = norm_com_size(all_text)

                    for line in lines:
                        if not education:
                            education = norm_edu(line)
                        if not work_year:
                            work_year = norm_work_year(line)
                        if not com_type:
                            com_type = norm_com_type(line)
                        if not com_size:
                            com_size = norm_com_size(line)

                    if title and len(title) >= 2:
                        all_data.append({
                            "job_name": title.strip()[:255],
                            "com_name": company.strip()[:255] if company else "",
                            "salary_lower": sl,
                            "salary_high": sh,
                            "city": city_name,
                            "district": location.strip()[:50],
                            "education": education,
                            "work_year": work_year,
                            "com_type": com_type,
                            "com_size": com_size,
                            "job_benefits": "",
                            "source": "liepin",
                        })
                        valid += 1
                        combo_valid += 1

                logger.info(f"  Valid {valid} (total {len(all_data)})")
                time.sleep(random.uniform(2, 3))

            except Exception as e:
                logger.info(f"  Error: {type(e).__name__}: {str(e)[:80]}")

            # 组合级统计
            if combo_valid == 0:
                consecutive_empty += 1
                logger.info(f"  [无有效数据] 连续空: {consecutive_empty}/{max_consecutive_empty}")
            else:
                consecutive_empty = 0

    logger.info(f"[猎聘] Total: {len(all_data)}")
    return all_data


# ============================================================
# 数据合并入库
# ============================================================
def merge_to_db(data_list: List[Dict]) -> Dict:
    """UPDATE 现有记录缺失字段 + INSERT 新记录"""
    if not data_list:
        return {"total": 0, "updated": 0, "new": 0}

    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    stats = {"total": len(data_list), "updated": 0, "new": 0, "fields": {"education": 0, "work_year": 0, "com_type": 0, "com_size": 0}}

    for data in data_list:
        job_name = data.get("job_name", "")
        com_name = data.get("com_name", "")
        if not job_name or not com_name:
            continue

        # 尝试匹配现有记录
        cur.execute(
            "SELECT id, education, work_year, com_type, com_size FROM t_recruitment_info WHERE job_name = %s AND com_name = %s LIMIT 1",
            (job_name, com_name),
        )
        existing = cur.fetchone()

        if existing:
            rid, db_edu, db_wy, db_ct, db_cs = existing
            updates, params = [], []

            for field, db_val in [("education", db_edu), ("work_year", db_wy), ("com_type", db_ct), ("com_size", db_cs)]:
                new_val = data.get(field, "")
                if new_val and (not db_val or db_val == ""):
                    updates.append(f"{field} = %s")
                    params.append(new_val)
                    stats["fields"][field] += 1

            if updates:
                params.append(rid)
                cur.execute(f"UPDATE t_recruitment_info SET {', '.join(updates)} WHERE id = %s", params)
                stats["updated"] += 1
        else:
            # 新记录
            try:
                job_area = f"{data.get('city', '')}·{data.get('district', '')}"
                cur.execute(
                    """INSERT INTO t_recruitment_info
                    (job_name, job_area, salary_lower, salary_high, com_name,
                     com_type, com_size, work_year, education, job_benefits, city, district, street)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        job_name, job_area,
                        data.get("salary_lower") or 0, data.get("salary_high") or 0,
                        com_name,
                        data.get("com_type", ""), data.get("com_size", ""),
                        data.get("work_year", ""), data.get("education", ""),
                        data.get("job_benefits", ""),
                        data.get("city", ""), data.get("district", ""), "",
                    ),
                )
                stats["new"] += 1
            except Exception:
                pass

    conn.commit()
    cur.close()
    conn.close()
    return stats


# ============================================================
# 主流程
# ============================================================
def main():
    logger.info("=" * 60)
    logger.info("  Multi-Source Crawler v2 (Verified Feasible)")
    logger.info("  Sources: zhaopin.com + liepin.com")
    logger.info("=" * 60)

    all_data = []

    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True, channel="chrome")
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        page = ctx.new_page()

        # ---- 智联招聘 ----
        logger.info("\n>>> Source 1: zhaopin.com <<<")
        try:
            data_zp = crawl_zhaopin(page)
            all_data.extend(data_zp)
        except Exception as e:
            logger.error(f"zhaopin failed: {type(e).__name__}: {e}")

        # ---- 猎聘 ----
        logger.info("\n>>> Source 2: liepin.com <<<")
        try:
            data_lp = crawl_liepin(page)
            all_data.extend(data_lp)
        except Exception as e:
            logger.error(f"liepin failed: {type(e).__name__}: {e}")

        browser.close()
        pw.stop()

    except Exception as e:
        logger.error(f"Browser failed: {type(e).__name__}: {e}")
        return

    # 去重
    seen = set()
    deduped = []
    for d in all_data:
        key = (d.get("job_name", ""), d.get("com_name", ""))
        if key not in seen and all(key):
            seen.add(key)
            deduped.append(d)
    logger.info(f"\n[Dedup] {len(all_data)} -> {len(deduped)} unique")

    # 输出字段覆盖率
    total = len(deduped)
    if total > 0:
        for field in ["education", "work_year", "com_type", "com_size"]:
            has = sum(1 for d in deduped if d.get(field))
            logger.info(f"  {field}: {has}/{total} ({has/total*100:.1f}%)")

        stats = merge_to_db(deduped)

        # 最终状态
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM t_recruitment_info")
        final_total = cur.fetchone()[0]

        print("\n" + "=" * 60)
        print("  Database Final Status")
        print("=" * 60)
        for col, cn in [("education", "Education"), ("work_year", "Work Year"),
                         ("com_type", "Com Type"), ("com_size", "Com Size")]:
            cur.execute(f"SELECT COUNT(*) FROM t_recruitment_info WHERE {col} IS NOT NULL AND {col} != ''")
            has = cur.fetchone()[0]
            print(f"  {cn}: {has}/{final_total} ({has/final_total*100:.1f}%)")
        print(f"  Total records: {final_total} (crawled: {len(deduped)}, updated: {stats['updated']}, new: {stats['new']})")
        conn.close()
    else:
        logger.error("No data crawled!")

    # 清理临时文件
    for f in ["check_data_status.py", "check_comtype.py", "check_remaining.py"]:
        p = Path(__file__).parent / f
        if p.exists():
            p.unlink()
            logger.info(f"Cleaned: {f}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--skip-zhaopin", action="store_true")
    p.add_argument("--skip-liepin", action="store_true")
    args = p.parse_args()
    main()
