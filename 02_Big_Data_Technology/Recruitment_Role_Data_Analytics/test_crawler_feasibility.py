# -*- coding: utf-8 -*-
"""快速可行性验证 - 测试每个数据源是否可访问，选择器是否有效"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import re
from playwright.sync_api import sync_playwright

print("=" * 60)
print("  多源爬虫可行性验证")
print("=" * 60)

# Step 1: Playwright
print("\n[1] Check Playwright Browser...")
try:
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True, channel="chrome")
    print("  [OK] Chrome launched successfully")
except Exception as e:
    print(f"  [FAIL] Chrome: {e}")
    try:
        browser = pw.chromium.launch(headless=True)
        print("  [OK] Chromium (built-in) launched")
    except Exception as e2:
        print(f"  [FATAL] Cannot start browser: {e2}")
        exit(1)

context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="zh-CN",
)
page = context.new_page()

# ============================================================
# Step 2: 51job search page
# ============================================================
print("\n[2] Test 51job Search Page...")
try:
    url = "https://we.51job.com/pc/search?keyword=数据分析&jobArea=010000"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)

    title = page.title()
    print(f"  Page title: {title}")

    cards = page.evaluate("() => document.querySelectorAll('.joblist-item').length")
    print(f"  .joblist-item count: {cards}")

    if cards > 0:
        sample = page.evaluate("""() => {
            const el = document.querySelector('.joblist-item');
            return {
                title: el.querySelector('.job-title, .jname')?.innerText?.trim() || '',
                company: el.querySelector('.cname')?.innerText?.trim() || '',
                salary: el.querySelector('.sal, .salary')?.innerText?.trim() || '',
                area: el.querySelector('.area')?.innerText?.trim() || '',
                tags: [...el.querySelectorAll('.tags span, .tag')].map(t => t.innerText.trim()).join('/'),
                com_info: el.querySelector('.com-info')?.innerText?.trim() || '',
            };
        }""")
        print(f"  Sample job: {sample.get('title', 'N/A')[:50]}")
        print(f"  Sample company: {sample.get('company', 'N/A')[:50]}")
        print(f"  Sample salary: {sample.get('salary', 'N/A')}")
        print(f"  Sample area: {sample.get('area', 'N/A')}")
        print(f"  Sample tags: {sample.get('tags', 'N/A')[:80]}")
        print(f"  Com info: {sample.get('com_info', 'N/A')[:80]}")
        print("  [OK] 51job search page works")

        # Check detail link
        detail_link = page.evaluate("""() => {
            const el = document.querySelector('.joblist-item a[href]');
            return el ? el.href : null;
        }""")
        print(f"  Detail link: {detail_link}")
    else:
        print("  [FAIL] .joblist-item not found - page structure may have changed")

except Exception as e:
    print(f"  [FAIL] 51job access error: {type(e).__name__}: {str(e)[:120]}")

# ============================================================
# Step 3: 51job detail page
# ============================================================
print("\n[3] Test 51job Detail Page...")
try:
    detail_link = page.evaluate("""() => {
        const el = document.querySelector('.joblist-item a[href]');
        return el ? el.href : null;
    }""")

    if detail_link:
        page.goto(detail_link, wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)

        detail_info = page.evaluate("""() => {
            const getText = (sel) => { const el = document.querySelector(sel); return el ? el.innerText.trim() : ''; };
            return {
                title: getText('.jname') || getText('h1') || getText('.job-name'),
                jobMsg: getText('.job-msg') || getText('.job_info') || getText('.job-detail-header'),
                comInfo: getText('.com-msg') || getText('.com-info'),
                bodyText: document.body.innerText.substring(0, 800),
            };
        }""")
        print(f"  Detail title: {detail_info.get('title', 'N/A')[:60]}")
        print(f"  Job info: {detail_info.get('jobMsg', 'N/A')[:120]}")
        print(f"  Company info: {detail_info.get('comInfo', 'N/A')[:120]}")

        body = detail_info.get('bodyText', '')
        edu_match = re.search(r'本科|硕士|大专|博士|学历不限', body)
        exp_match = re.search(r'应届|(\d+-\d+年)|\d+年以上|经验不限', body)
        size_match = re.search(r'(\d+人以上|\d+-\d+人|\d+-\d+人)', body)

        print(f"  Education found: {'YES' if edu_match else 'NO'} -> {edu_match.group() if edu_match else 'none'}")
        print(f"  Experience found: {'YES' if exp_match else 'NO'} -> {exp_match.group() if exp_match else 'none'}")
        print(f"  Size found: {'YES' if size_match else 'NO'} -> {size_match.group() if size_match else 'none'}")

        if edu_match or exp_match or size_match:
            print("  [OK] 51job detail pages have the missing fields")
        else:
            print("  [WARN] No usable fields found in detail page body")
            print(f"  Body preview: {body[:300]}...")
    else:
        print("  [FAIL] No detail link found from search page")
except Exception as e:
    print(f"  [FAIL] 51job detail error: {type(e).__name__}: {str(e)[:120]}")

# ============================================================
# Step 4: Liepin
# ============================================================
print("\n[4] Test Liepin (liepin.com)...")
try:
    url = "https://www.liepin.com/zhaopin/?key=数据分析&dqs=010"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)
    title = page.title()
    print(f"  Page title: {title}")

    selectors = [
        ('.job-list-item', 'search result card'),
        ('.job-card', 'legacy card'),
        ('[class*="job-list"] > div', 'job list container'),
        ('.left-list-box > div', 'left list box'),
        ('.job-info-box', 'job info box'),
        ('[class*="job"]', 'generic job elements'),
    ]
    for sel, desc in selectors:
        count = page.evaluate(f"() => document.querySelectorAll('{sel}').length")
        print(f"  {sel} ({desc}): {count}")

    body_text = page.evaluate("() => document.body.innerText.substring(0, 600)")
    print(f"  Body start: {body_text[:300]}...")

    if any(kw in body_text for kw in ["验证", "滑块", "captcha"]):
        print("  [FAIL] Anti-bot verification triggered")
    elif "数据分析" in body_text:
        print("  [OK] Liepin accessible with search results")
    else:
        print("  [WARN] Page state uncertain")

except Exception as e:
    print(f"  [FAIL] Liepin error: {type(e).__name__}: {str(e)[:120]}")

# ============================================================
# Step 5: Lagou
# ============================================================
print("\n[5] Test Lagou (lagou.com)...")
try:
    url = "https://www.lagou.com/wn/jobs?kd=数据分析&city=北京&pn=1"
    page.goto(url, wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)
    title = page.title()
    print(f"  Page title: {title}")

    for sel in ['.job-card', '.item__10RTO', '.position-item', '[class*="job"]']:
        count = page.evaluate(f"() => document.querySelectorAll('{sel}').length")
        if count > 0:
            print(f"  {sel}: {count}")

    body_text = page.evaluate("() => document.body.innerText.substring(0, 600)")
    print(f"  Body start: {body_text[:300]}...")

    if any(kw in body_text for kw in ["验证", "滑块", "captcha"]):
        print("  [FAIL] Anti-bot verification triggered")
    elif "数据分析" in body_text:
        print("  [OK] Lagou accessible")

        sample = page.evaluate("""() => {
            const card = document.querySelector('.job-card, .item__10RTO, .position-item');
            if (!card) return null;
            const title = card.querySelector('[class*="name"]')?.innerText?.trim() || '';
            const salary = card.querySelector('[class*="salary"], .money')?.innerText?.trim() || '';
            const labels = [...card.querySelectorAll('.item-label, .labels li, [class*="label"]')].map(t => t.innerText.trim());
            return {title, salary, labels};
        }""")
        if sample:
            print(f"  Sample job: {sample.get('title', 'N/A')}")
            print(f"  Sample salary: {sample.get('salary', 'N/A')}")
            print(f"  Sample labels: {sample.get('labels', [])}")
    else:
        print("  [WARN] Page state uncertain")

except Exception as e:
    print(f"  [FAIL] Lagou error: {type(e).__name__}: {str(e)[:120]}")

# ============================================================
# Cleanup
# ============================================================
browser.close()
pw.stop()

print("\n" + "=" * 60)
print("  Feasibility Test Complete")
print("=" * 60)
