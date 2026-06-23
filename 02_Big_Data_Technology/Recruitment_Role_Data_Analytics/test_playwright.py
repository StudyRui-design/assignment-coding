# -*- coding: utf-8 -*-
"""测试 Playwright 浏览器是否可用 + 测试51job爬取"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright
import time

print("=== 测试1: 系统 Chrome 浏览器是否可用 ===")
try:
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        channel="chrome",   # 使用系统安装的 Chrome
        headless=True,
    )
    print("  [OK] Chrome 启动成功")

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    print("  [OK] 浏览器上下文创建成功")

    # 测试1: 51job 新版搜索页
    print("\n=== 测试2: 51job 新版搜索页 ===")
    url = "https://we.51job.com/pc/search?keyword=数据分析&jobArea=010000"
    try:
        print(f"  正在访问: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print(f"  最终 URL: {page.url[:80]}")
        print(f"  Title: {page.title()}")

        # 等待搜索结果列表加载
        time.sleep(6)

        html = page.content()
        print(f"  页面长度: {len(html)} 字符")
        print(f"  包含 aliyun_waf: {'aliyun_waf' in html.lower()}")
        print(f"  包含 __NUXT__: {'__NUXT__' in html}")
        print(f"  包含 _51job_: {'51job' in html.lower()}")

        # 尝试抓取岗位信息
        selectors = [
            ".joblist-item",
            ".job-card",
            "[class*='job']",
            ".j_joblist",
            ".joblist",
            "div.el",
            ".joblist_item",
            ".job-card-container",
            ".result-job",
            ".job-info",
        ]
        found_any = False
        for sel in selectors:
            cards = page.query_selector_all(sel)
            if cards:
                print(f"  选择器 '{sel}' 匹配到 {len(cards)} 个元素")
                for i, card in enumerate(cards[:3]):
                    text = card.inner_text()[:150].replace('\n', ' | ')
                    print(f"    [{i}] {text}")
                found_any = True
                break

        if not found_any:
            print("  未匹配到任何岗位卡片选择器")
            body_text = page.inner_text("body")[:600]
            print(f"  页面文本预览 (前600字):")
            print(f"    {body_text}")

    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")

    # 测试2: 招聘网站
    print("\n=== 测试3: 招聘网站搜索页 ===")
    try:
        url2 = "https://www.zhipin.com/web/geek/job?query=数据分析&city=101010100"
        print(f"  正在访问: {url2}")
        page.goto(url2, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        html = page.content()
        print(f"  页面长度: {len(html)} 字符")
        print(f"  Title: {page.title()}")
        print(f"  最终 URL: {page.url[:80]}")

        body_text = page.inner_text("body")[:600]
        print(f"  页面文本 (前600字):")
        print(f"    {body_text}")
    except Exception as e:
        print(f"  [FAIL] {type(e).__name__}: {e}")

    browser.close()
    pw.stop()

except Exception as e:
    print(f"  [FAIL] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
