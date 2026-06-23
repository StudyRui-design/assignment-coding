# -*- coding: utf-8 -*-
"""
修复数据库中 com_type 和 com_size 字段
1. 从 CSV 中提取 公司名→类型/规模 的映射
2. 对数据库中匹配到的公司名直接回填
3. 对未匹配的用关键词规则推断
"""
import csv
import pymysql
import re
from collections import defaultdict

DB_CONFIG = {
    "host": "localhost", "user": "root", "password": "123456",
    "db": "recruitment_db", "charset": "utf8mb4",
}

# ===== 1. 从 CSV 提取公司→类型映射 =====
csv_map = {}  # com_name -> (com_type, com_size)
with open("全国-热门城市岗位数据.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("com_name", "").strip()
        ct = row.get("com_type", "").strip()
        cs = row.get("com_size", "").strip()
        if name and ct:
            csv_map[name] = (ct, cs)

print(f"[1] 从CSV提取到 {len(csv_map)} 条公司→类型映射")
print(f"    样本: {list(csv_map.items())[:5]}")

# ===== 2. 关键词 → 企业类型 推断规则 =====
# 优先级从高到低
TYPE_KEYWORDS = [
    (r"人工智能|AI|深度学习|机器学习|NLP|计算机视觉|大模型|算法", "人工智能"),
    (r"半导体|芯片|集成电路|微电子|电子股份|电子集团|电子有限|电子\（|恩斯迈", "半导体/电子"),
    (r"互联网|网络科技|网络技术|信息技术|信息科技|科技信息|软件|大数据|数字|云计算|数据科技|数智|智联|在线|平台|电商|游戏|直播|移动|科技有限|科技股份|科技集团|科技\（|数据股份|数据产业|信息产业|数科", "互联网"),
    (r"通信|电信|移动|联通|广电|5G|通讯", "通信/电子"),
    (r"银行|金融|保险|证券|基金|投资|信托|资管|支付|理财|期货|金服|融租|担保", "金融"),
    (r"医药|制药|生物|医疗|健康|基因|药|医|生命科学", "医疗/医药"),
    (r"汽车|新能源|锂电|电池|充电|电动车|自动驾驶|车联", "汽车/新能源"),
    (r"教育|培训|学校|大学|学院|留学|在线教育|教辅", "教育/培训"),
    (r"咨询|顾问|咨询管理|管理咨询|信息咨询|猎头|人力|HR|招聘|人才服务|人力资源", "咨询/服务"),
    (r"房地产|地产|置业|物业|房产|建筑|装饰|工程|施工|设计院|建设集团|城建", "房地产/建筑"),
    (r"零售|贸易|进出口|外贸|商贸|百货|超市|便利|连锁|餐饮|食品|饮料|电商平台", "商贸/零售"),
    (r"制造|工厂|生产|机械|设备|仪器|自动化|电气|精密|加工", "制造业"),
    (r"物流|快递|运输|航空|海运|供应链|仓储|配送|货运", "物流/运输"),
    (r"传媒|广告|媒体|文化|影视|娱乐|出版|动漫|设计|创意|品牌|公关|营销", "传媒/文化"),
    (r"能源|电力|石油|石化|燃气|煤炭|矿产|水利", "能源/化工"),
    (r"法律|律师|律所|法务|知识产权|专利", "法律/专业服务"),
    (r"政府|事业|研究院|研究所|科研|实验室", "科研/事业单位"),
    # 宽泛兜底规则（优先级最低）
    (r"科技|数据|数智|智能|信息", "互联网"),
]

SIZE_KEYWORDS = [
    (r"10000人以上|10000以上|万人以上|10000\s*以上", "10000人以上"),
    (r"5000[\s-]*10000人|5000-10000", "5000-10000人"),
    (r"1000[\s-]*5000人|1000-5000|千人", "1000-5000人"),
    (r"500[\s-]*999人|500-999", "500-999人"),
    (r"100[\s-]*499人|100-499", "100-499人"),
    (r"50[\s-]*99人|少于50人|少于100人|50人以下", "50-99人"),
    (r"上市公司|上市|A股|港股|美股|纳斯达克", "大型企业"),
    (r"外资|外商|欧美|日企|韩企|德资|法资|500强", "外资企业"),
    (r"国企|央企|国有|国资", "国有企业"),
    (r"民营|私企", "民营企业"),
    (r"创业|初创|天使|A轮|B轮|C轮|Pre-IPO", "初创/成长型"),
]


def infer_com_type(company_name: str) -> str:
    """根据公司名称推断企业类型"""
    for pattern, label in TYPE_KEYWORDS:
        if re.search(pattern, company_name):
            return label
    return ""


def infer_com_size(company_name: str) -> str:
    """根据公司名称推断企业规模"""
    for pattern, label in SIZE_KEYWORDS:
        if re.search(pattern, company_name):
            return label
    return ""


# ===== 3. 连接数据库并修复 =====
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()

# 查所有记录
cur.execute("SELECT id, com_name, com_type, com_size FROM t_recruitment_info")
all_rows = cur.fetchall()
print(f"\n[2] 数据库总计 {len(all_rows)} 条记录")

# 分类计数
matched_csv = 0
inferred = 0
remaining = 0

updates = []  # (com_type, com_size, id)

for row_id, com_name, cur_ct, cur_cs in all_rows:
    # 跳过已有数据的
    if cur_ct and cur_ct != "":
        continue

    ct = ""
    cs = ""

    # 先尝试 CSV 精确匹配
    if com_name in csv_map:
        ct, cs = csv_map[com_name]
        matched_csv += 1
    else:
        # 关键词推断
        ct = infer_com_type(com_name)
        cs = infer_com_size(com_name)
        if ct:
            inferred += 1
        else:
            remaining += 1
            continue

    updates.append((ct, cs, row_id))

print(f"    CSV精确匹配: {matched_csv}")
print(f"    关键词推断: {inferred}")
print(f"    无法推断: {remaining}")

# ===== 4. 批量更新 =====
if updates:
    for ct, cs, row_id in updates:
        cur.execute(
            "UPDATE t_recruitment_info SET com_type=%s, com_size=%s WHERE id=%s",
            (ct, cs, row_id),
        )

    conn.commit()
    print(f"\n[3] 已更新 {len(updates)} 条记录")

    # ===== 5. 验证结果 =====
    cur.execute("SELECT com_type, COUNT(*) as cnt FROM t_recruitment_info WHERE com_type != '' GROUP BY com_type ORDER BY cnt DESC")
    rows = cur.fetchall()
    print(f"\n[4] 修复后企业类型分布:")
    print(f"    {'企业类型':20s} | 数量")
    print(f"    {'-'*35}")
    for r in rows:
        print(f"    {r[0]:20s} | {r[1]}")

    cur.execute("SELECT COUNT(*) FROM t_recruitment_info WHERE com_type IS NULL OR com_type=''")
    null_count = cur.fetchone()[0]
    total = len(all_rows)
    print(f"\n    有数据: {total - null_count}/{total}, 覆盖率: {(total - null_count)/total*100:.1f}%")
else:
    print("\n[3] 无需更新（所有记录可能已有 com_type 数据）")

conn.close()
print("\n[完成] com_type 修复完毕！")
