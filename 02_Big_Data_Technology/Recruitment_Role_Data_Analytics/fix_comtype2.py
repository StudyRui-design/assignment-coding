import pymysql
conn = pymysql.connect(host='localhost', user='root', password='123456', db='recruitment_db', charset='utf8mb4')
cur = conn.cursor()
cur.execute("UPDATE t_recruitment_info SET com_type='互联网' WHERE com_type='互联网/IT'")
print(f"合并互联网/IT -> 互联网: {cur.rowcount} 条")
conn.commit()

# 重新跑fix_comtype的推断逻辑（仅对剩余空值）
import csv, re
csv_map = {}
with open("全国-热门城市岗位数据.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("com_name", "").strip()
        ct = row.get("com_type", "").strip()
        cs = row.get("com_size", "").strip()
        if name and ct:
            csv_map[name] = (ct, cs)

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
    (r"科技|数据|数智|智能|信息", "互联网"),
]

def infer_com_type(company_name):
    for pattern, label in TYPE_KEYWORDS:
        if re.search(pattern, company_name):
            return label
    return ""

# 查剩余空值
cur.execute("SELECT id, com_name FROM t_recruitment_info WHERE com_type = '' OR com_type IS NULL")
rows = cur.fetchall()
print(f"\n剩余空值: {len(rows)}")

updates = 0
for rid, name in rows:
    ct = infer_com_type(name)
    if ct:
        cur.execute("UPDATE t_recruitment_info SET com_type=%s WHERE id=%s", (ct, rid))
        updates += 1

conn.commit()
print(f"补充更新: {updates} 条")

# 最终统计
cur.execute("SELECT com_type, COUNT(*) as cnt FROM t_recruitment_info WHERE com_type != '' GROUP BY com_type ORDER BY cnt DESC")
rows2 = cur.fetchall()
print(f"\n最终企业类型分布:")
for r in rows2:
    print(f"  {r[0]:20s} | {r[1]}")

cur.execute("SELECT COUNT(*) FROM t_recruitment_info WHERE com_type IS NULL OR com_type=''")
null_count = cur.fetchone()[0]
total = cur.execute("SELECT COUNT(*) FROM t_recruitment_info")
cur.execute("SELECT COUNT(*) FROM t_recruitment_info")
total = cur.fetchone()[0]
print(f"\n有数据: {total - null_count}/{total}, 覆盖率: {(total - null_count)/total*100:.1f}%")
conn.close()
