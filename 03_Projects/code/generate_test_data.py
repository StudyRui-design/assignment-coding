# -*- coding: utf-8 -*-
"""
大数据测试数据生成脚本
为Spark大数据分析平台生成丰富的测试数据

使用方法:
    python generate_test_data.py

生成数据量:
    - 用户: 200人
    - 科目: 30门
    - 学习记录: 5000条
    - 用户行为特征: 200条
    - 用户评分: 3000条
"""

import mysql.connector
import random
from datetime import datetime, timedelta

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'test',
    'charset': 'utf8mb4'
}

# ==================== 数据定义 ====================

# 姓氏
SURNAMES = ['张', '王', '李', '刘', '陈', '杨', '赵', '黄', '周', '吴',
            '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
            '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧',
            '程', '曹', '袁', '邓', '许', '傅', '沈', '曾', '彭', '吕']

# 名字
NAMES = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋',
         '勇', '艳', '杰', '娟', '涛', '明', '超', '秀', '霞', '平',
         '刚', '桂', '英', '华', '建', '文', '辉', '玲', '婷', '宇',
         '浩', '欣', '雨', '晨', '轩', '昊', '瑞', '嘉', '逸', '博',
         '雅', '诗', '涵', '梓', '萱', '怡', '彤', '曦', '妍', '琳']

# 科目数据（30门）
SUBJECTS = [
    ('Java程序设计', '王教授'),
    ('Python数据分析', '李老师'),
    ('高等数学', '张教授'),
    ('大学英语', '陈老师'),
    ('数据结构', '刘教授'),
    ('操作系统', '赵老师'),
    ('计算机网络', '孙教授'),
    ('数据库原理', '周老师'),
    ('Web前端开发', '吴老师'),
    ('机器学习基础', '郑教授'),
    ('深度学习实战', '钱教授'),
    ('大数据技术', '冯老师'),
    ('云计算概论', '于老师'),
    ('信息安全', '董教授'),
    ('软件工程', '萧老师'),
    ('算法设计与分析', '程教授'),
    ('人工智能导论', '曹老师'),
    ('自然语言处理', '袁教授'),
    ('计算机图形学', '邓老师'),
    ('物联网技术', '许老师'),
    ('区块链技术', '傅教授'),
    ('移动应用开发', '沈老师'),
    ('游戏开发入门', '曾老师'),
    ('数字图像处理', '彭老师'),
    ('嵌入式系统', '吕老师'),
    ('微服务架构', '王老师'),
    ('DevOps实践', '李老师'),
    ('敏捷开发方法', '张老师'),
    ('项目管理', '陈老师'),
    ('技术写作', '刘老师'),
]

# 课件文件名模板
STUDY_TEMPLATES = [
    '{}第{}章课件', '{}实验指导{}', '{}项目实战{}',
    '{}复习资料{}', '{}课后习题{}', '{}案例分析{}',
    '{}视频教程{}', '{}参考文档{}', '{}练习题库{}',
    '{}期末复习{}'
]

# 课件描述模板
DESCRIPTIONS = [
    '本课件详细介绍了{}的核心概念和基本原理',
    '通过实际案例深入理解{}的应用场景',
    '{}基础入门到进阶的完整学习资料',
    '包含{}的重点难点解析和练习题',
    '{}实验操作步骤和注意事项说明',
]


def get_connection():
    """获取数据库连接"""
    return mysql.connector.connect(**DB_CONFIG)


def generate_username(existing_names):
    """生成唯一的用户名"""
    while True:
        surname = random.choice(SURNAMES)
        name = random.choice(NAMES)
        username = surname + name + str(random.randint(10, 99))
        if username not in existing_names:
            existing_names.add(username)
            return username


def generate_real_name():
    """生成真实姓名"""
    surname = random.choice(SURNAMES)
    name = random.choice(NAMES)
    if random.random() > 0.5:
        name += random.choice(NAMES)
    return surname + name


def generate_phone():
    """生成手机号"""
    prefixes = ['138', '139', '135', '136', '137', '150', '151', '152',
                '157', '158', '159', '182', '183', '187', '188', '130',
                '131', '132', '155', '156', '185', '186', '133', '153',
                '180', '189']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_email(username):
    """生成邮箱"""
    domains = ['@qq.com', '@163.com', '@gmail.com', '@outlook.com', '@126.com']
    return username + random.choice(domains)


def random_date(start_date, end_date):
    """生成随机日期"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


def truncate_table(cursor, table_name):
    """清空表数据"""
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        print(f"  [OK] 已清空表: {table_name}")
    except Exception as e:
        print(f"  清空表 {table_name} 失败: {e}")


def create_tables(cursor):
    """创建必要的表"""
    print("\n=== 创建数据表 ===")

    # user表 - 先删除旧表再创建，确保字段一致
    cursor.execute('DROP TABLE IF EXISTS user')
    cursor.execute('''
    CREATE TABLE user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL DEFAULT '123456',
        real_name VARCHAR(50),
        email VARCHAR(100),
        phone VARCHAR(20),
        age INT DEFAULT 20,
        gender VARCHAR(10) DEFAULT '男',
        major VARCHAR(50) DEFAULT '计算机科学与技术',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT '正常'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')
    print("  [OK] user 表已创建")

    # subject表
    cursor.execute('DROP TABLE IF EXISTS subject')
    cursor.execute('''
    CREATE TABLE subject (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL COMMENT '科目名称',
        creator VARCHAR(50) COMMENT '创建人',
        description TEXT COMMENT '科目描述',
        credit INT DEFAULT 3 COMMENT '学分',
        hours INT DEFAULT 48 COMMENT '课时',
        status VARCHAR(20) DEFAULT '正常' COMMENT '状态',
        category VARCHAR(50) DEFAULT '专业必修' COMMENT '类别',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')
    print("  [OK] subject 表已创建")

    # study表（课件/学习记录）
    cursor.execute('DROP TABLE IF EXISTS study')
    cursor.execute('''
    CREATE TABLE study (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(200) NOT NULL COMMENT '课件资源名',
        subject_id INT COMMENT '所属科目ID',
        subject_name VARCHAR(100) COMMENT '所属科目名称',
        description TEXT COMMENT '课件简介',
        detail TEXT COMMENT '课件详情',
        attachment VARCHAR(200) COMMENT '课件附件',
        upload_date DATE COMMENT '上传日期',
        upload_user VARCHAR(50) COMMENT '上传用户',
        file_size INT DEFAULT 1024 COMMENT '文件大小KB',
        download_count INT DEFAULT 0 COMMENT '下载次数',
        duration INT DEFAULT 45 COMMENT '学习时长分钟',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')
    print("  [OK] study 表已创建")

    # user_behavior_feature表（用户行为特征）
    cursor.execute('DROP TABLE IF EXISTS user_behavior_feature')
    cursor.execute('''
    CREATE TABLE user_behavior_feature (
        user_id INT PRIMARY KEY,
        total_study_count INT DEFAULT 0 COMMENT '总学习次数',
        total_subjects INT DEFAULT 0 COMMENT '学习过的科目数',
        avg_study_per_subject FLOAT DEFAULT 0 COMMENT '每科目平均学习次数',
        recent_activity_days INT DEFAULT 0 COMMENT '最近活跃天数',
        activity_ratio FLOAT DEFAULT 0 COMMENT '活跃度比例',
        total_duration INT DEFAULT 0 COMMENT '总学习时长分钟',
        avg_rating FLOAT DEFAULT 0 COMMENT '平均评分',
        last_study_date DATE COMMENT '最后学习日期',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')
    print("  [OK] user_behavior_feature 表已创建")

    # user_subject_rating表（用户评分）
    cursor.execute('DROP TABLE IF EXISTS user_subject_rating')
    cursor.execute('''
    CREATE TABLE user_subject_rating (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT COMMENT '用户ID',
        subject_id INT COMMENT '科目ID',
        rating FLOAT COMMENT '评分1-5',
        interaction_count INT DEFAULT 1 COMMENT '交互次数',
        comment TEXT COMMENT '评价内容',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_user_subject (user_id, subject_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ''')
    print("  [OK] user_subject_rating 表已创建")


def generate_users(cursor, count=200):
    """生成用户数据"""
    print(f"\n=== 生成用户数据 ({count}人) ===")
    existing_names = set()
    users = []

    majors = ['计算机科学与技术', '软件工程', '网络工程', '信息安全',
              '数据科学与大数据技术', '人工智能', '物联网工程']
    genders = ['男', '女']

    for i in range(count):
        username = generate_username(existing_names)
        real_name = generate_real_name()
        email = generate_email(username)
        phone = generate_phone()
        age = random.randint(18, 25)
        gender = random.choice(genders)
        major = random.choice(majors)

        users.append((username, '123456', real_name, email, phone, age, gender, major))

    sql = '''INSERT INTO user (username, password, real_name, email, phone, age, gender, major)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.executemany(sql, users)
    print(f"  [OK] 已插入 {count} 条用户数据")
    return count


def generate_subjects(cursor):
    """生成科目数据"""
    print(f"\n=== 生成科目数据 ({len(SUBJECTS)}门) ===")
    categories = ['专业必修', '专业选修', '公共必修', '公共选修']
    subjects_data = []

    for i, (name, creator) in enumerate(SUBJECTS, 1):
        description = f"本课程系统讲解{name}的理论知识和实践技能"
        credit = random.choice([2, 3, 4])
        hours = credit * 16
        category = random.choice(categories)
        subjects_data.append((name, creator, description, credit, hours, category))

    sql = '''INSERT INTO subject (name, creator, description, credit, hours, category)
             VALUES (%s, %s, %s, %s, %s, %s)'''
    cursor.executemany(sql, subjects_data)
    print(f"  [OK] 已插入 {len(SUBJECTS)} 条科目数据")
    return len(SUBJECTS)


def generate_study_records(cursor, count=5000):
    """生成学习记录（课件数据）"""
    print(f"\n=== 生成学习记录 ({count}条) ===")

    # 获取所有用户和科目
    cursor.execute("SELECT id, username FROM user")
    users = cursor.fetchall()

    cursor.execute("SELECT id, name FROM subject")
    subjects = cursor.fetchall()

    records = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 5, 1)

    for i in range(count):
        user = random.choice(users)
        subject = random.choice(subjects)
        user_id, username = user
        subject_id, subject_name = subject

        # 生成课件信息
        template = random.choice(STUDY_TEMPLATES)
        chapter = random.randint(1, 12)
        filename = template.format(subject_name, chapter)

        description = random.choice(DESCRIPTIONS).format(subject_name)
        detail = f"{description}，适合{random.choice(['初学者', '进阶学习者', '复习备考'])}使用。"

        upload_date = random_date(start_date, end_date)
        file_size = random.randint(500, 10240)  # 500KB - 10MB
        download_count = random.randint(0, 500)
        duration = random.choice([30, 45, 60, 90, 120])  # 学习时长

        records.append((
            filename, subject_id, subject_name, description, detail,
            f"{filename}.pdf", upload_date, username, file_size, download_count, duration
        ))

    sql = '''INSERT INTO study (filename, subject_id, subject_name, description, detail,
                               attachment, upload_date, upload_user, file_size, download_count, duration)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.executemany(sql, records)
    print(f"  [OK] 已插入 {count} 条学习记录")
    return count


def generate_user_behavior_features(cursor):
    """生成用户行为特征数据"""
    print("\n=== 生成用户行为特征数据 ===")

    cursor.execute("SELECT id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM subject")
    subject_ids = [row[0] for row in cursor.fetchall()]

    features = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 5, 1)

    for user_id in user_ids:
        # 随机决定用户活跃度类型
        user_type = random.random()

        if user_type < 0.15:  # 15% 新手用户
            total_study_count = random.randint(0, 5)
            total_subjects = random.randint(0, 2)
            recent_activity_days = random.randint(0, 3)
            activity_ratio = round(random.uniform(0, 0.1), 2)
        elif user_type < 0.35:  # 20% 沉默用户
            total_study_count = random.randint(5, 20)
            total_subjects = random.randint(1, 5)
            recent_activity_days = random.randint(0, 7)
            activity_ratio = round(random.uniform(0.05, 0.2), 2)
        elif user_type < 0.70:  # 35% 普通用户
            total_study_count = random.randint(20, 80)
            total_subjects = random.randint(5, 15)
            recent_activity_days = random.randint(7, 20)
            activity_ratio = round(random.uniform(0.2, 0.5), 2)
        else:  # 30% 活跃用户
            total_study_count = random.randint(80, 200)
            total_subjects = random.randint(10, 25)
            recent_activity_days = random.randint(20, 30)
            activity_ratio = round(random.uniform(0.5, 1.0), 2)

        avg_study_per_subject = round(total_study_count / max(total_subjects, 1), 2)
        total_duration = total_study_count * random.randint(30, 60)
        avg_rating = round(random.uniform(3.0, 5.0), 1)
        last_study_date = random_date(start_date, end_date)

        features.append((
            user_id, total_study_count, total_subjects, avg_study_per_subject,
            recent_activity_days, activity_ratio, total_duration, avg_rating, last_study_date
        ))

    sql = '''INSERT INTO user_behavior_feature
             (user_id, total_study_count, total_subjects, avg_study_per_subject,
              recent_activity_days, activity_ratio, total_duration, avg_rating, last_study_date)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cursor.executemany(sql, features)
    print(f"  [OK] 已插入 {len(features)} 条用户行为特征数据")
    return len(features)


def generate_user_ratings(cursor, count=3000):
    """生成用户评分数据"""
    print(f"\n=== 生成用户评分数据 ({count}条) ===")

    cursor.execute("SELECT id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM subject")
    subject_ids = [row[0] for row in cursor.fetchall()]

    comments = [
        '课程内容很实用，老师讲解清晰',
        '难度适中，适合初学者入门',
        '案例丰富，理论与实践结合得很好',
        '课件制作精美，学习体验很好',
        '课程结构清晰，循序渐进',
        '实战项目很有帮助',
        '老师经验丰富，讲解深入浅出',
        '课程更新及时，紧跟技术发展',
        '互动性强，学习氛围好',
        '作业设计合理，巩固效果好',
        '内容有些偏难，需要多花时间',
        '希望能增加更多实战案例',
        '整体不错，推荐学习',
        '课程质量很高，收获很大',
        '讲解速度有点快，需要反复观看',
    ]

    ratings_data = []
    used_pairs = set()

    for i in range(count):
        # 确保每对(user_id, subject_id)唯一
        while True:
            user_id = random.choice(user_ids)
            subject_id = random.choice(subject_ids)
            pair = (user_id, subject_id)
            if pair not in used_pairs:
                used_pairs.add(pair)
                break

        # 评分分布：大部分在3-5分之间
        rating_random = random.random()
        if rating_random < 0.05:
            rating = 1.0
        elif rating_random < 0.10:
            rating = 2.0
        elif rating_random < 0.30:
            rating = 3.0
        elif rating_random < 0.60:
            rating = 4.0
        else:
            rating = 5.0

        interaction_count = random.randint(1, 50)
        comment = random.choice(comments)

        ratings_data.append((user_id, subject_id, rating, interaction_count, comment))

    sql = '''INSERT INTO user_subject_rating (user_id, subject_id, rating, interaction_count, comment)
             VALUES (%s, %s, %s, %s, %s)'''
    cursor.executemany(sql, ratings_data)
    print(f"  [OK] 已插入 {count} 条用户评分数据")
    return count


def print_statistics(cursor):
    """打印数据统计信息"""
    print("\n=== 数据统计 ===")

    tables = ['user', 'subject', 'study', 'user_behavior_feature', 'user_subject_rating']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:30s}: {count:6d} 条记录")

    print("\n=== 数据分布 ===")

    # 用户活跃度分布
    cursor.execute('''
        SELECT 
            CASE 
                WHEN activity_ratio > 0.5 THEN '活跃用户'
                WHEN activity_ratio > 0.2 THEN '普通用户'
                WHEN total_study_count > 0 THEN '沉默用户'
                ELSE '新手用户'
            END as user_type,
            COUNT(*) as count
        FROM user_behavior_feature
        GROUP BY user_type
    ''')
    print("\n  用户活跃度分布:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]}人")

    # 科目评分分布
    cursor.execute('''
        SELECT 
            CASE 
                WHEN rating >= 4.5 THEN '优秀(4.5-5.0)'
                WHEN rating >= 3.5 THEN '良好(3.5-4.5)'
                WHEN rating >= 2.5 THEN '一般(2.5-3.5)'
                ELSE '较差(<2.5)'
            END as rating_level,
            COUNT(*) as count
        FROM user_subject_rating
        GROUP BY rating_level
    ''')
    print("\n  评分分布:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]}条")


def main():
    """主函数"""
    print("=" * 60)
    print("  Spark大数据分析平台 - 测试数据生成工具")
    print("=" * 60)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 创建表
        create_tables(cursor)

        # 清空现有数据
        print("\n=== 清空现有数据 ===")
        for table in ['user_subject_rating', 'user_behavior_feature', 'study', 'subject', 'user']:
            truncate_table(cursor, table)

        # 生成数据
        generate_users(cursor, 200)
        generate_subjects(cursor)
        generate_study_records(cursor, 5000)
        generate_user_behavior_features(cursor)
        generate_user_ratings(cursor, 3000)

        conn.commit()

        # 打印统计
        print_statistics(cursor)

        print("\n" + "=" * 60)
        print("  数据生成完成！")
        print("=" * 60)
        print("\n  请按以下步骤启动项目:")
        print("  1. 启动 MySQL 数据库")
        print("  2. 启动 Spark 微服务 (端口9090)")
        print("  3. 启动 JavaWeb 项目 (端口8080)")
        print("  4. 访问 http://localhost:8080/sft/bigData.html")
        print("=" * 60)

    except Exception as e:
        print(f"\n  错误: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
