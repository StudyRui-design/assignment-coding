# -*- coding: utf-8 -*-
"""
大数据测试数据生成脚本（适配本系统实际表结构）
生成丰富的测试数据供大数据分析平台使用

使用方法:
    python generate_test_data.py
"""

import pymysql
import random
import hashlib
from datetime import datetime, timedelta
from faker import Faker

# ==================== 配置 ====================
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "test",
    "charset": "utf8mb4",
}

USER_COUNT = 200
STUDY_RECORD_COUNT = 5000
RATING_COUNT = 3000

fake = Faker("zh_CN")

# ==================== 数据定义 ====================
USER_TYPES = ["学员", "教师", "管理员"]
GENDERS = ["男", "女"]

SUBJECTS = [
    ("Java程序设计", "王教授"),
    ("Python数据分析", "李老师"),
    ("高等数学", "张教授"),
    ("大学英语", "陈老师"),
    ("数据结构", "刘教授"),
    ("操作系统", "赵老师"),
    ("计算机网络", "孙教授"),
    ("数据库原理", "周老师"),
    ("Web前端开发", "吴老师"),
    ("机器学习基础", "郑教授"),
    ("深度学习实战", "钱教授"),
    ("大数据技术", "冯老师"),
    ("云计算概论", "于老师"),
    ("信息安全", "董教授"),
    ("软件工程", "萧老师"),
    ("算法设计与分析", "程教授"),
    ("人工智能导论", "曹老师"),
    ("自然语言处理", "袁教授"),
    ("计算机图形学", "邓老师"),
    ("物联网技术", "许老师"),
    ("区块链技术", "傅教授"),
    ("移动应用开发", "沈老师"),
    ("游戏开发入门", "曾老师"),
    ("数字图像处理", "彭老师"),
    ("嵌入式系统", "吕老师"),
    ("微服务架构", "王老师"),
    ("DevOps实践", "李老师"),
    ("Spark大数据分析", "冯老师"),
    ("数据可视化技术", "吴老师"),
]

STUDY_TEMPLATES = [
    "{}课件_第{}章", "{}实验指导_实验{}", "{}课后习题{}",
    "{}笔记_{}", "{}项目源码_{}", "{}学习总结_{}",
    "{}参考资料_{}", "{}练习题_{}", "{}复习大纲_{}",
]


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def generate_users(conn):
    """生成200个用户"""
    print("[INFO] 正在生成 {} 个用户...".format(USER_COUNT))
    users = []
    existing_usernames = set()
    
    with conn.cursor() as cur:
        # 获取已存在的用户名
        cur.execute("SELECT username FROM user")
        for row in cur.fetchall():
            existing_usernames.add(row[0])
        
        # 获取当前最大ID
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM user")
        max_id = cur.fetchone()[0]
        
        count = 0
        for i in range(1, USER_COUNT + 1):
            username = "student{:03d}".format(i)
            if username in existing_usernames:
                continue
            count += 1
            uid = max_id + count
            real_name = fake.name()
            gender = random.choice(GENDERS)
            birth = "{}-{:02d}-{:02d}".format(
                random.randint(1998, 2005),
                random.randint(1, 12),
                random.randint(1, 28)
            )
            phone = "1{:02d}{:08d}".format(random.randint(30, 99), random.randint(0, 99999999))
            address = fake.address()
            user_type = "学员" if i > 3 else random.choice(USER_TYPES)
            
            # 使用 MD5 哈希与 SQL init 脚本保持一致
            pwd_md5 = hashlib.md5('123456'.encode('utf-8')).hexdigest()
            cur.execute(
                """INSERT INTO user (id, username, password, real_name, gender, birth, phone, address, user_type)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, username, pwd_md5, real_name, gender, birth, phone, address, user_type)
            )
            users.append({"id": uid, "username": username, "real_name": real_name, "user_type": user_type})
        
        conn.commit()
    
    print("[INFO] 实际新增 {} 个用户".format(count))
    return users


def generate_subjects(conn):
    """生成科目（保留原有 + 新增）"""
    print("[INFO] 正在处理科目数据 ({}门)...".format(len(SUBJECTS)))
    subject_ids = []
    
    with conn.cursor() as cur:
        # 获取已有科目
        cur.execute("SELECT id, name FROM subject")
        existing = {row[1]: row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM subject")
        max_id = cur.fetchone()[0]
        
        new_count = 0
        for i, (name, creator) in enumerate(SUBJECTS, 1):
            if name in existing:
                subject_ids.append(existing[name])
            else:
                new_count += 1
                sid = max_id + new_count
                cur.execute(
                    "INSERT INTO subject (id, name, creator, status) VALUES (%s, %s, %s, '正常')",
                    (sid, name, creator)
                )
                subject_ids.append(sid)
        
        conn.commit()
    
    print("[INFO] 现有 {} 门, 新增 {} 门, 共 {} 门科目".format(
        len(subject_ids) - new_count, new_count, len(subject_ids)))
    return subject_ids


def generate_study_records(conn, users, subject_ids):
    """生成5000条学习记录"""
    print("[INFO] 正在生成 {} 条学习记录...".format(STUDY_RECORD_COUNT))
    batch = []
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM study")
        existing_count = cur.fetchone()[0]
        if existing_count >= STUDY_RECORD_COUNT:
            print("[INFO] 已有 {} 条学习记录，跳过".format(existing_count))
            return
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2025, 5, 1)
        
        # 获取科目名称映射
        cur.execute("SELECT id, name FROM subject")
        subject_names = {row[0]: row[1] for row in cur.fetchall()}
        
        for i in range(STUDY_RECORD_COUNT):
            user = random.choice(users)
            subject_id = random.choice(subject_ids)
            subject_name = subject_names.get(subject_id, "通用")
            
            template = random.choice(STUDY_TEMPLATES)
            chapter = random.randint(1, 15)
            title = template.format(subject_name, chapter)
            
            summary = "{}上传的{} - 适合学习参考".format(user["real_name"], subject_name)
            content = "本课件详细讲解了{}的相关知识点，包含理论讲解和实战案例。".format(subject_name)
            file_src = "{}_{}.pdf".format(subject_name, chapter)
            
            # 随机日期
            days_between = (end_date - start_date).days
            upload_date = start_date + timedelta(days=random.randint(0, days_between))
            
            duration = random.choice([30, 45, 60, 90, 120])
            download_count = random.randint(0, 500)
            
            batch.append((
                title, subject_id, subject_name, summary, content, file_src,
                user["username"], upload_date, download_count, duration
            ))
            
            if len(batch) >= 500:
                cur.executemany(
                    """INSERT INTO study (title, subject_id, subject_name, summary, content, file_src,
                                          creator, create_time, download_count, duration)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    batch
                )
                conn.commit()
                batch = []
                print("  ... 已生成 {}/{} 条记录".format(i + 1, STUDY_RECORD_COUNT))
        
        if batch:
            cur.executemany(
                """INSERT INTO study (title, subject_id, subject_name, summary, content, file_src,
                                      creator, create_time, download_count, duration)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                batch
            )
            conn.commit()
    
    print("[INFO] {} 条学习记录生成完成".format(STUDY_RECORD_COUNT))


def generate_behavior_features(conn, users):
    """填充用户行为特征表（从study表聚合计算）"""
    print("[INFO] 正在计算用户行为特征...")
    
    with conn.cursor() as cur:
        # 清空重建
        cur.execute("DELETE FROM user_behavior_feature")
        
        # 从 study 表聚合计算
        cur.execute("""
            INSERT INTO user_behavior_feature 
                (user_id, total_study_count, total_study_hours, avg_study_duration,
                 study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label)
            SELECT
                u.id,
                COUNT(st.id),
                COALESCE(SUM(st.duration), 0) / 60.0,
                ROUND(COALESCE(AVG(st.duration), 0), 2),
                COUNT(DISTINCT DATE(st.create_time)),
                COUNT(CASE WHEN st.create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 END),
                COUNT(DISTINCT st.subject_id),
                ROUND(RAND() * 30),
                0,
                -1
            FROM user u
            LEFT JOIN study st ON u.username = st.creator
            WHERE u.user_type = '学员'
            GROUP BY u.id
            HAVING COUNT(st.id) > 0
        """)
        conn.commit()
        
        # 为没有学习记录的用户也生成特征（新手用户）
        cur.execute("""
            INSERT IGNORE INTO user_behavior_feature 
                (user_id, total_study_count, total_study_hours, avg_study_duration,
                 study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label)
            SELECT id, 0, 0, 0, 0, 0, 0, 0, 0, -1
            FROM user
            WHERE user_type = '学员'
              AND id NOT IN (SELECT user_id FROM user_behavior_feature)
        """)
        
        # 随机增强部分用户的行为特征（模拟不同活跃度）
        cur.execute("SELECT user_id, total_study_count FROM user_behavior_feature")
        for row in cur.fetchall():
            uid = row[0]
            base_count = row[1]
            if base_count == 0:
                # 新手用户：随机补充少量特征
                total = random.randint(1, 5)
                hours = total * random.randint(20, 40) / 60.0
                cur.execute(
                    """UPDATE user_behavior_feature SET
                       total_study_count = GREATEST(total_study_count, %s),
                       total_study_hours = GREATEST(total_study_hours, %s),
                       avg_study_duration = ROUND(%s / GREATEST(%s, 1), 2),
                       study_days = GREATEST(study_days, %s),
                       subject_count = GREATEST(subject_count, %s),
                       max_consecutive_days = 0
                       WHERE user_id = %s""",
                    (total, hours, hours * 60, total, random.randint(1, 3), random.randint(1, 5), uid)
                )
            elif base_count < 20:
                # 沉默用户 → 补充数据
                extra = random.randint(5, 20)
                cur.execute(
                    """UPDATE user_behavior_feature SET
                       total_study_count = total_study_count + %s,
                       total_study_hours = total_study_hours + RAND() * 5,
                       subject_count = LEAST(subject_count + %s, 10)
                       WHERE user_id = %s""",
                    (extra, random.randint(1, 5), uid)
                )
        
        # 更新平均评分
        cur.execute("""
            UPDATE user_behavior_feature ubf
            LEFT JOIN (
                SELECT user_id, ROUND(AVG(rating), 2) AS avg_r
                FROM user_subject_rating
                GROUP BY user_id
            ) r ON ubf.user_id = r.user_id
            SET ubf.avg_score = COALESCE(ROUND(r.avg_r, 2), ROUND(RAND() * 3 + 2, 2))
        """)
        
        conn.commit()
    
    # 统计各类用户
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM user_behavior_feature")
        count = cur.fetchone()[0]
        cur.execute("""
            SELECT cluster_label, COUNT(*) FROM user_behavior_feature GROUP BY cluster_label
        """)
        print("[INFO] 行为特征表: {} 条记录".format(count))
        for row in cur.fetchall():
            print("    cluster {}: {} 人".format(row[0], row[1]))


def generate_ratings(conn, users, subject_ids):
    """生成3000条评分记录"""
    print("[INFO] 正在生成 {} 条评分记录...".format(RATING_COUNT))
    
    student_users = [u for u in users if u["user_type"] == "学员"]
    if not student_users:
        student_users = users
    
    comments = [
        '课程内容很实用，老师讲解清晰',
        '难度适中，适合初学者入门',
        '案例丰富，理论与实践结合得很好',
        '课程结构清晰，循序渐进',
        '实战项目很有帮助',
        '老师经验丰富，讲解深入浅出',
        '整体不错，推荐学习',
        '课程质量很高，收获很大',
        '内容有些偏难，需要多花时间',
        '希望能增加更多实战案例',
    ]
    
    used_pairs = set()
    batch = []
    
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_subject_rating")
        
        for i in range(RATING_COUNT):
            while True:
                user = random.choice(student_users)
                subject_id = random.choice(subject_ids)
                pair = (user["id"], subject_id)
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    break
            
            # 评分分布（偏向高分）
            rating = random.choices(
                [1.0, 2.0, 3.0, 4.0, 5.0],
                weights=[0.05, 0.10, 0.20, 0.35, 0.30]
            )[0]
            rating = min(rating + random.uniform(0, 0.9), 5.0)
            rating = round(rating, 1)
            
            interaction_count = random.randint(1, 50)
            comment = random.choice(comments)
            
            batch.append((user["id"], subject_id, rating, interaction_count, comment))
            
            if len(batch) >= 500:
                cur.executemany(
                    """INSERT INTO user_subject_rating
                       (user_id, subject_id, rating, interaction_count, comment, created_at)
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    batch
                )
                conn.commit()
                batch = []
                print("  ... 已生成 {} 条评分".format(len(used_pairs)))
        
        if batch:
            cur.executemany(
                """INSERT INTO user_subject_rating
                   (user_id, subject_id, rating, interaction_count, comment, created_at)
                   VALUES (%s, %s, %s, %s, %s, NOW())""",
                batch
            )
            conn.commit()
    
    print("[INFO] {} 条评分记录生成完成".format(RATING_COUNT))


def update_cluster_labels(conn):
    """更新聚类标签（基于活跃度规则）"""
    print("[INFO] 正在计算用户聚类标签...")
    
    with conn.cursor() as cur:
        # 活跃用户: study_days > 15
        cur.execute("""
            UPDATE user_behavior_feature
            SET cluster_label = '活跃用户'
            WHERE study_days > 15
        """)
        active = cur.rowcount
        
        # 普通用户: study_days > 5 且 <= 15
        cur.execute("""
            UPDATE user_behavior_feature
            SET cluster_label = '普通用户'
            WHERE study_days > 5 AND study_days <= 15
        """)
        normal = cur.rowcount
        
        # 沉默用户: total_study_count > 0 且 study_days <= 5
        cur.execute("""
            UPDATE user_behavior_feature
            SET cluster_label = '沉默用户'
            WHERE total_study_count > 0 AND study_days <= 5
        """)
        silent = cur.rowcount
        
        # 新手用户: 无学习记录
        cur.execute("""
            UPDATE user_behavior_feature
            SET cluster_label = '新手用户'
            WHERE total_study_count = 0
        """)
        newbie = cur.rowcount
        
        conn.commit()
    
    print("[INFO] 聚类标签更新完成:")
    print("    活跃用户: {}".format(active))
    print("    普通用户: {}".format(normal))
    print("    沉默用户: {}".format(silent))
    print("    新手用户: {}".format(newbie))


def print_statistics(conn):
    """打印统计信息"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM user")
        user_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM subject")
        subj_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM study")
        study_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM user_behavior_feature")
        feat_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM user_subject_rating")
        rating_cnt = cur.fetchone()[0]
        
        # 用户类型分布
        cur.execute("SELECT user_type, COUNT(*) FROM user GROUP BY user_type")
        user_types = cur.fetchall()
        
        # 评分分布
        cur.execute("""
            SELECT CASE 
                WHEN rating >= 4.0 THEN '高分(4.0-5.0)'
                WHEN rating >= 3.0 THEN '中分(3.0-4.0)'
                WHEN rating >= 2.0 THEN '低分(2.0-3.0)'
                ELSE '极低(<2.0)'
            END AS level, COUNT(*)
            FROM user_subject_rating
            GROUP BY level
        """)
        rating_dist = cur.fetchall()
    
    print("=" * 55)
    print("  Spark大数据分析 - 测试数据生成统计")
    print("=" * 55)
    print("  [用户] 总用户数:      {}".format(user_cnt))
    for ut, cnt in user_types:
        print("    ├ {}: {}人".format(ut, cnt))
    print("  [科目] 科目数:        {}".format(subj_cnt))
    print("  [学习] 学习记录:      {}".format(study_cnt))
    print("  [特征] 行为特征:      {}".format(feat_cnt))
    print("  [评分] 评分记录:      {}".format(rating_cnt))
    print("  [评分分布]")
    for level, cnt in rating_dist:
        print("    ├ {}: {}条".format(level, cnt))
    print("=" * 55)
    print("  访问地址:")
    print("    首页:         http://localhost:8080/sft/")
    print("    大数据分析:   http://localhost:8080/sft/bigData.html")
    print("    智能推荐:     http://localhost:8080/sft/machineLearning.html")
    print("    Spark API:    http://localhost:9090/api/stats/overview")
    print("=" * 55)


def main():
    print("=" * 55)
    print("  大数据技术开发实训 - 测试数据生成工具 v2")
    print("  适配本系统实际数据库结构")
    print("=" * 55)
    
    conn = get_connection()
    try:
        # 1. 生成用户（保留现有，新增测试用户）
        users = generate_users(conn)
        if not users:
            print("[WARN] 没有新增用户，使用全部用户")
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, real_name, user_type FROM user")
                users = [{"id": r[0], "username": r[1], "real_name": r[2], "user_type": r[3]} for r in cur.fetchall()]
        
        # 2. 生成科目
        subject_ids = generate_subjects(conn)
        
        # 3. 生成学习记录
        generate_study_records(conn, users, subject_ids)
        
        # 4. 生成评分
        generate_ratings(conn, users, subject_ids)
        
        # 5. 生成行为特征
        generate_behavior_features(conn, users)
        
        # 6. 更新聚类标签
        update_cluster_labels(conn)
        
        # 7. 打印统计
        print_statistics(conn)
        
    except Exception as e:
        print("\n[ERROR] 数据生成失败: {}".format(e))
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
