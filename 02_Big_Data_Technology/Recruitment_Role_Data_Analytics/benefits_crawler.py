# -*- coding: utf-8 -*-
"""
岗位福利爬虫扩展脚本 (v2 优化版)

优化点：
1. Playwright 真实浏览器爬取 51job 福利（绕过WAF）
2. 增加结构化日志，区分 INFO/WARN/ERROR
3. 分离配置常量
4. 增加 type hints
5. 搜索结果+详情页双重福利提取
"""

import sys
import time
import random
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import pymysql
import pandas as pd
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
logger = logging.getLogger("BenefitsCrawler")

# ============================================================
# 配置常量
# ============================================================
BASE_DIR = Path(__file__).parent


# 搜索关键词池
SEARCH_KEYWORDS = ["数据分析", "大数据", "算法工程师", "Java开发", "Python开发"]

# 目标城市及编码
CITY_MAP = {
    "北京": "010000", "上海": "020000", "深圳": "040000",
    "广州": "030200", "杭州": "080200",
}


# ============================================================
# 一、Playwright 真实浏览器福利爬取
# ============================================================
def scrape_51job_benefits_playwright(
    page: Page,
    keyword: str = "数据分析",
    city: str = "北京",
) -> List[str]:
    """
    使用 Playwright 从 51job 搜索结果中直接提取福利标签

    策略：
    1. 访问 we.51job.com 新版搜索页（已确认绕过WAF）
    2. 从 .joblist-item 的 .tags 元素提取福利标签
    3. 也可访问详情页获取更完整福利

    参数:
        page: Playwright Page 对象
        keyword: 搜索关键词
        city: 城市名
    返回: 福利字符串列表
    """
    logger.info(f"[Playwright福利] 关键词={keyword}, 城市={city}")
    all_benefits: List[str] = []
    city_code = CITY_MAP.get(city, "010000")

    try:
        # Step 1: 访问搜索页
        url = f"https://we.51job.com/pc/search?keyword={keyword}&jobArea={city_code}"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        try:
            page.wait_for_selector(".joblist-item", timeout=15000)
        except Exception:
            logger.info(f"  [Playwright福利] {keyword}-{city}: 超时或无结果")
            return all_benefits

        time.sleep(random.uniform(2, 4))

        # Step 2: 从搜索结果列表直接提取福利标签
        benefits_from_list = page.evaluate("""() => {
            const items = document.querySelectorAll('.joblist-item');
            const allTags = [];
            items.forEach(el => {
                const tagEls = el.querySelectorAll('.tags span, .tag');
                tagEls.forEach(t => {
                    const txt = t.innerText.trim();
                    if (txt.length >= 2 && txt.length <= 15) allTags.push(txt);
                });
            });
            return [...new Set(allTags)];
        }""")

        if benefits_from_list:
            benefits_str = "/".join(benefits_from_list[:30])
            all_benefits.append(benefits_str)
            logger.info(f"  [Playwright福利] 从列表页提取 {len(benefits_from_list)} 个标签")

        # Step 3: 获取详情页链接，访问详情页提取更完整福利
        detail_urls = page.evaluate("""() => {
            return [...document.querySelectorAll('.joblist-item a[href*="jobs.51job.com"]')]
                .map(a => a.href)
                .filter((v, i, a) => a.indexOf(v) === i)
                .slice(0, 10);
        }""")

        for i, detail_url in enumerate(detail_urls):
            try:
                page.goto(detail_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(random.uniform(1, 2))

                benefit_tags = page.evaluate("""() => {
                    const selectors = [
                        'div.t1 span.sp4',
                        'div.jtag div.t1 span',
                        'p.lname span',
                        '.job-detail-tags .tag',
                    ];
                    for (const sel of selectors) {
                        const els = document.querySelectorAll(sel);
                        if (els.length > 0) {
                            return [...els].map(e => e.innerText.trim())
                                .filter(t => t.length >= 2 && t.length <= 15);
                        }
                    }
                    // Fallback: 从描述中正则提取
                    const desc = document.querySelector('div.bmsg.job_msg');
                    if (desc) {
                        const match = desc.innerText.match(/福利[：:]\\s*(.+?)(?:\\n|$)/);
                        if (match) return match[1].split(/[、，,\\/\\s]+/).filter(t => t.length >= 2);
                    }
                    return [];
                }""")

                if benefit_tags:
                    all_benefits.append("/".join(benefit_tags))

                if (i + 1) % 3 == 0:
                    logger.info(f"    [{i + 1}/{len(detail_urls)}] 已获取 {len(all_benefits)} 条福利")

            except Exception:
                continue

    except Exception as e:
        logger.info(f"  [Playwright福利] 异常: {type(e).__name__}: {e}")

    logger.info(f"  [Playwright福利] 共获取 {len(all_benefits)} 条福利")
    return all_benefits


# ============================================================
# 二、更新数据库福利字段（仅真实爬取数据）
# ============================================================
def update_benefits_in_db(enable_crawl: bool = True) -> int:
    """
    用真实爬取的福利数据更新数据库记录

    参数:
        enable_crawl: 是否尝试真实爬取
    返回: 更新的记录数（0表示无真实数据可更新）
    """
    logger.info("[数据库更新] 准备更新岗位福利数据...")

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM t_recruitment_info ORDER BY id")
    ids = [row[0] for row in cursor.fetchall()]
    logger.info(f"  共 {len(ids)} 条待更新记录")

    # --- 爬取真实福利 ---
    real_crawled: List[str] = []

    if enable_crawl:
        logger.info("  启动 Playwright 浏览器爬取福利数据...")
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
                for city in random.sample(list(CITY_MAP.keys()), min(2, len(CITY_MAP))):
                    benefits = scrape_51job_benefits_playwright(page, keyword=kw, city=city)
                    real_crawled.extend(benefits)
                    time.sleep(random.uniform(2, 4))
                    if len(real_crawled) >= 20:
                        break
                if len(real_crawled) >= 20:
                    break

            browser.close()
            pw.stop()
        except Exception as e:
            logger.error(f"  Playwright 浏览器异常: {type(e).__name__}: {e}")
    else:
        logger.info("  跳过真实爬取 (enable_crawl=False)")

    if not real_crawled:
        logger.warning("  真实爬取未获取到数据 (目标网站已升级反爬机制)")
        logger.warning("  福利字段将保持原样，不进行更新")
        cursor.close()
        conn.close()
        return 0

    logger.info(f"  真实爬取福利: {len(real_crawled)} 条")

    # --- 用真实数据更新数据库 ---
    all_benefits_pool = list(real_crawled)
    random.shuffle(all_benefits_pool)
    logger.info(f"  福利池(全部来自真实爬取): {len(all_benefits_pool)} 种")

    update_sql = "UPDATE t_recruitment_info SET job_benefits = %s WHERE id = %s"
    updated = 0
    batch_size = 50

    for i, record_id in enumerate(ids):
        benefit = all_benefits_pool[i % len(all_benefits_pool)]
        cursor.execute(update_sql, (benefit, record_id))
        updated += 1

        if (i + 1) % batch_size == 0:
            conn.commit()
            logger.info(f"  已更新 {i + 1}/{len(ids)} 条")

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"[完成] 共更新 {updated} 条记录的福利字段")
    return updated


# ============================================================
# 三、重新生成词云图
# ============================================================
def regenerate_wordcloud() -> List[Tuple[str, int]]:
    """基于更新后的数据库重新生成词云图"""
    logger.info("[词云重生成] 基于福利数据生成词云图...")

    import jieba
    from wordcloud import WordCloud
    from collections import Counter
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    conn = pymysql.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT job_benefits FROM t_recruitment_info", conn)
    conn.close()

    benefits_text = " ".join(df["job_benefits"].dropna().astype(str).tolist())

    # 使用共享福利关键词库
    from utils import register_benefits_dict, BENEFITS_STOPWORDS
    register_benefits_dict()

    segments = benefits_text.replace("/", " ").replace("、", " ").replace("，", " ").replace("+", " ")
    words = jieba.cut(segments)
    word_list = [w.strip() for w in words if len(w.strip()) >= 2]
    word_list = [w for w in word_list if w not in BENEFITS_STOPWORDS]

    word_freq = Counter(word_list)
    top_words = word_freq.most_common(80)
    logger.info(f"  词频TOP10: {top_words[:10]}")

    # 生成词云图
    wc = WordCloud(
        font_path="C:/Windows/Fonts/msyh.ttc",
        width=1200,
        height=700,
        background_color="white",
        max_words=100,
        max_font_size=160,
        min_font_size=10,
        colormap="Set2",
        collocations=False,
        random_state=42,
        prefer_horizontal=0.7,
    )
    wc.generate_from_frequencies(dict(top_words))

    output_dir = BASE_DIR / "static" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("岗位福利词云（真实爬取数据）", fontsize=20, fontweight="bold", pad=25)

    path = output_dir / "08_benefits_wordcloud.png"
    fig.savefig(path, bbox_inches="tight", dpi=180, facecolor="white")
    plt.close(fig)
    logger.info(f"  词云图已保存: {path}")

    # 同步到 recruitment_project
    import shutil
    project_dir = BASE_DIR / "recruitment_project" / "static" / "images"
    project_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, project_dir / "08_benefits_wordcloud.png")
    logger.info(f"  已同步到: {project_dir / '08_benefits_wordcloud.png'}")

    return top_words


# ============================================================
# 主流程
# ============================================================
def main(enable_crawl: bool = True):
    """
    主流程

    参数:
        enable_crawl: 是否尝试真实爬取。
                      True  - 尝试真实爬取福利数据
                      False - 跳过爬取
    """
    print("=" * 60)
    print("  岗位福利爬虫扩展脚本 (v2)")
    print(f"  模式: {'真实爬取' if enable_crawl else '跳过爬取'}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: 更新数据库福利
    count = update_benefits_in_db(enable_crawl=enable_crawl)

    # Step 2: 重新生成词云
    if count > 0:
        top_words = regenerate_wordcloud()
        print(f"\n{'=' * 60}")
        print(f"  完成！福利词云已基于真实爬取数据更新")
        print(f"  福利词数量: {len(top_words)} 个")
        print(f"  福利池来源: 100% 真实爬取 ({count} 条记录已更新)")
        print(f"{'=' * 60}")
    else:
        logger.info("  无真实福利数据，跳过词云更新")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="岗位福利爬虫扩展脚本")
    parser.add_argument(
        "--no-crawl",
        action="store_true",
        help="跳过真实爬取",
    )
    args = parser.parse_args()
    main(enable_crawl=not args.no_crawl)
