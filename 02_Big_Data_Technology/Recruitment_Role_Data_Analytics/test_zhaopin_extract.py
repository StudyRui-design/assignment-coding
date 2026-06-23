# -*- coding: utf-8 -*-
"""快速测试: 智联招聘单页数据提取"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True, channel="chrome")
ctx = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="zh-CN",
)
page = ctx.new_page()

url = "https://sou.zhaopin.com/?jl=530&kw=数据分析&p=1"
print(f"Loading: {url}")
page.goto(url, wait_until="domcontentloaded", timeout=30000)
time.sleep(3)

# 方法1: 查找可能的选择器
page_html = page.evaluate("() => document.body.innerHTML.substring(0, 3000)")
import re

# 找 class 中含有 job/position/card/list 的元素
classes = set(re.findall(r'class="([^"]*)"', page_html))
relevant = [c for c in classes if any(k in c.lower() for k in ['job', 'position', 'card', 'list', 'item'])]
print(f"\nRelevant classes in body: {relevant[:30]}")

# 方法2: 直接用body文本提取结构化数据
body = page.evaluate("() => document.body.innerText")
print(f"\nBody preview (first 1000 chars):")
print(body[:1000])
print(f"\n---")

# 方法3: 使用更精确的JS提取
jobs = page.evaluate("""() => {
    // 尝试多种可能的选择器
    let cards = [];
    const selectors = [
        '.joblist-box__item', '.positionlist .positionlist__item',
        '.joblist-box > div', '[class*="joblist"] > div',
        '.searchResultList div[class*="item"]',
        '[class*="positionCard"]', '.resultlist__item',
    ];

    for (const sel of selectors) {
        try {
            const els = document.querySelectorAll(sel);
            if (els.length >= 3) {
                cards = [...els].slice(0, 10).map(el => ({
                    selector: sel,
                    text: el.innerText?.substring(0, 300) || '',
                    html: el.outerHTML?.substring(0, 500) || '',
                }));
                break;
            }
        } catch(e) {}
    }

    // 如果上面的找不到，尝试遍历body里的div
    if (cards.length === 0) {
        const bodyText = document.body.innerText;
        const lines = bodyText.split('\\n').filter(l => l.trim().length > 0);
        cards = [{
            selector: 'body text lines',
            text: lines.slice(0, 50).join('\\n'),
            html: '',
            lineCount: lines.length,
            lines: lines.slice(0, 50),
        }];
    }

    return cards;
}""")

for i, card in enumerate(jobs[:5]):
    print(f"\nCard [{i}] selector={card.get('selector')}:")
    print(f"  Text: {card.get('text', '')[:300]}")

# 输出完整文本行，分析结构
lines = body.split('\n')
lines = [l.strip() for l in lines if l.strip()]
print(f"\nTotal non-empty lines: {len(lines)}")
print("First 40 lines:")
for i, line in enumerate(lines[:40]):
    print(f"  [{i}] {line}")

browser.close()
pw.stop()
