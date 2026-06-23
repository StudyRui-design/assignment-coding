# -*- coding: utf-8 -*-
"""测试新版智联模式匹配解析器"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

# 导入爬虫模块的函数
from multi_source_crawler import (_parse_zhaopin_card, parse_salary,
    norm_edu, norm_work_year, norm_com_size, norm_com_type)

pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True, channel="chrome")
ctx = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    viewport={"width": 1920, "height": 1080},
    locale="zh-CN",
)
page = ctx.new_page()

url = "https://sou.zhaopin.com/?jl=530&kw=数据分析&p=1"
page.goto(url, wait_until="networkidle", timeout=45000)
time.sleep(3)

cards = page.evaluate("""() => {
    return [...document.querySelectorAll('.joblist-box__item')].map(el => {
        const raw = (el.innerText || '').trim();
        return raw.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
    });
}""")

print(f"Cards: {len(cards)}")
print("=" * 80)

stats = {"total": 0, "education": 0, "work_year": 0, "com_type": 0, "com_size": 0, "salary": 0, "company": 0}
errors = []

for i, lines in enumerate(cards):
    parsed = _parse_zhaopin_card(lines)
    sl, sh = parse_salary(parsed.get("salary_str", ""))

    edu = norm_edu(parsed.get("education_raw", ""))
    wy = norm_work_year(parsed.get("work_year_raw", ""))
    ct = norm_com_type(parsed.get("com_type_raw", ""))
    cs = norm_com_size(parsed.get("com_size_raw", ""))
    co = parsed.get("company", "")
    loc = parsed.get("location", "")

    all_text = " ".join(lines)
    if not edu: edu = norm_edu(all_text)
    if not wy: wy = norm_work_year(all_text)
    if not ct: ct = norm_com_type(all_text)
    if not cs: cs = norm_com_size(all_text)

    stats["total"] += 1
    if edu: stats["education"] += 1
    if wy: stats["work_year"] += 1
    if ct: stats["com_type"] += 1
    if cs: stats["com_size"] += 1
    if sl and sh: stats["salary"] += 1
    if co: stats["company"] += 1

    # 标记异常
    issues = []
    if not co: issues.append("NO_COMPANY")
    if not sl: issues.append("NO_SALARY")
    if not edu: issues.append("NO_EDU")
    if not wy: issues.append("NO_WY")

    flag = " !!! " + ",".join(issues) if issues else ""
    print(f"[{i+1}] {parsed['job_name'][:40]}{flag}")
    print(f"    salary={parsed.get('salary_str','?')[:20]:<20} -> ({sl},{sh})K")
    print(f"    edu={edu:<8} wy={wy:<10} ct={ct:<12} cs={cs}")
    print(f"    company={co[:35]}")
    if len(lines) <= 6:
        print(f"    RAW lines: {lines}")

    if issues:
        errors.append({"idx": i+1, "issues": issues, "lines": lines, "parsed": parsed})

print("\n" + "=" * 80)
print(f"Field coverage: total={stats['total']}")
for f in ["education", "work_year", "com_type", "com_size", "salary", "company"]:
    rate = stats[f]/stats['total']*100 if stats['total'] > 0 else 0
    status = "[OK]" if rate > 80 else "[WARN]" if rate > 50 else "[FAIL]"
    print(f"  {status} {f}: {stats[f]}/{stats['total']} ({rate:.0f}%)")

if errors:
    print(f"\nErrors ({len(errors)} cards with issues):")
    for e in errors[:5]:
        print(f"  Card #{e['idx']}: {e['issues']}")
        print(f"    Parsed: {e['parsed']}")
        print(f"    Lines({len(e['lines'])}): {e['lines'][:8]}")

browser.close()
pw.stop()
