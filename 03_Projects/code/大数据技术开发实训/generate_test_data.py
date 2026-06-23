"""
============================================
大数据技术开发实训 - 测试数据生成脚本
============================================
功能: 生成用户、科目、学习记录、行为特征、评分等测试数据
数据量: 200用户 | 29科目 | 5000学习记录 | 200行为特征 | 3000评分

使用方法:
    pip install pymysql faker
    python generate_test_data.py

确保 MySQL 服务已启动且 spark_data.sql 已执行。
============================================
"""

import pymysql
import random
import datetime
from faker import Faker

# ==================== 配置 ====================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "test",
    "charset": "utf8mb4",
}

USER_COUNT = 200
STUDY_RECORD_COUNT = 5000
RATING_COUNT = 3000

fake = Faker("zh_CN")

# ==================== 专业/班级/用户类型 ====================
MAJORS = [
    "计算机科学与技术", "软件工程", "数据科学与大数据技术",
    "人工智能", "网络工程", "信息安全", "物联网工程", "数字媒体技术"
]

USER_TYPES = ["学生", "教师", "管理员"]

# ==================== 科目数据 (29门) ====================
SUBJECTS = [
    {"name": "Java程序设计", "creator": "王教授", "description": "Java语言基础、面向对象、集合框架、IO流、多线程编程", "credit": 4, "hours": 64, "category": "专业必修"},
    {"name": "Python数据分析", "creator": "李老师", "description": "Python基础、NumPy/Pandas数据处理、Matplotlib可视化", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "高等数学", "creator": "张教授", "description": "微积分、级数、微分方程等数学基础知识", "credit": 4, "hours": 64, "category": "公共必修"},
    {"name": "大学英语", "creator": "陈老师", "description": "英语听说读写综合能力培养", "credit": 2, "hours": 32, "category": "公共必修"},
    {"name": "数据结构", "creator": "刘教授", "description": "线性表、树、图、排序算法、查找算法", "credit": 4, "hours": 64, "category": "专业必修"},
    {"name": "操作系统", "creator": "赵老师", "description": "进程管理、内存管理、文件系统、I/O系统", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "计算机网络", "creator": "孙教授", "description": "TCP/IP协议栈、HTTP/HTTPS、网络安全基础", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "数据库原理", "creator": "周老师", "description": "关系代数、SQL、事务处理、索引优化", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "Web前端开发", "creator": "吴老师", "description": "HTML/CSS/JavaScript/Vue.js全栈开发", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "机器学习基础", "creator": "郑教授", "description": "监督学习、无监督学习、模型评估与调优", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "深度学习实战", "creator": "钱教授", "description": "CNN/RNN/Transformer原理与实践应用", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "大数据技术", "creator": "冯老师", "description": "Hadoop生态、Spark计算、实时数据处理", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "云计算概论", "creator": "于老师", "description": "IaaS/PaaS/SaaS、Docker/K8s容器技术", "credit": 2, "hours": 32, "category": "公共选修"},
    {"name": "信息安全", "creator": "董教授", "description": "密码学、网络攻防、安全协议、隐私保护", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "软件工程", "creator": "萧老师", "description": "敏捷开发、需求分析、设计模式、项目管理", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "算法设计与分析", "creator": "程教授", "description": "分治、贪心、动态规划、回溯算法", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "人工智能导论", "creator": "曹老师", "description": "AI发展史、知识表示、专家系统、搜索策略", "credit": 2, "hours": 32, "category": "公共选修"},
    {"name": "自然语言处理", "creator": "袁教授", "description": "文本分类、情感分析、命名实体识别、机器翻译", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "计算机图形学", "creator": "邓老师", "description": "渲染管线、着色器、光线追踪、GPU编程", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "物联网技术", "creator": "许老师", "description": "传感器、嵌入式开发、通信协议、边缘计算", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "区块链技术", "creator": "傅教授", "description": "共识机制、智能合约、DeFi应用开发", "credit": 2, "hours": 32, "category": "公共选修"},
    {"name": "移动应用开发", "creator": "沈老师", "description": "Android/iOS原生开发、Flutter跨平台", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "游戏开发入门", "creator": "曾老师", "description": "Unity引擎、物理系统、UI交互、发布流程", "credit": 3, "hours": 48, "category": "公共选修"},
    {"name": "数字图像处理", "creator": "彭老师", "description": "图像滤波、边缘检测、形态学、图像分割", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "嵌入式系统", "creator": "吕老师", "description": "ARM架构、RTOS、驱动开发、硬件接口", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "微服务架构", "creator": "王老师", "description": "Spring Cloud、服务治理、熔断限流、链路追踪", "credit": 3, "hours": 48, "category": "专业选修"},
    {"name": "DevOps实践", "creator": "李老师", "description": "CI/CD流水线、容器编排、监控告警、自动化测试", "credit": 2, "hours": 32, "category": "专业选修"},
    {"name": "Spark大数据分析", "creator": "冯老师", "description": "Spark SQL/MLlib/Streaming实战", "credit": 3, "hours": 48, "category": "专业必修"},
    {"name": "数据可视化技术", "creator": "吴老师", "description": "ECharts/D3.js/Tableau数据可视化", "credit": 2, "hours": 32, "category": "专业选修"},
]


def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def clear_test_data(conn):
    """清理已有测试数据（保留管理员账号）"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_subject_rating")
        cur.execute("DELETE FROM user_behavior_feature")
        cur.execute("DELETE FROM study WHERE creator NOT LIKE 'admin%'")
        cur.execute("DELETE FROM user WHERE id NOT IN (SELECT t.id FROM (SELECT id FROM user WHERE username='admin' OR user_type='管理员') t)")
        cur.execute("DELETE FROM subject WHERE id > 100")  # 清理扩展科目
    conn.commit()
    print("[INFO] 旧测试数据已清理")


def generate_users(conn):
    """生成200个测试用户"""
    print(f"[INFO] 正在生成 {USER_COUNT} 个用户...")
    users = []
    with conn.cursor() as cur:
        # 先获取现有最大ID
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM user")
        max_id_base = cur.fetchone()[0]

        for i in range(1, USER_COUNT + 1):
            uid = max_id_base + i
            username = f"student{i:03d}"
            real_name = fake.name()
            email = f"student{i:03d}@jxut.edu.cn"
            age = random.randint(18, 25)
            major = random.choice(MAJORS)
            user_type = "学生" if i > 5 else random.choice(USER_TYPES)
            status = "正常"
            created_at = fake.date_between(start_date="-2y", end_date="today")

            cur.execute(
                """INSERT INTO user (id, username, password, real_name, email, age, major, user_type, status, created_at)
                   VALUES (%s, %s, '123456', %s, %s, %s, %s, %s, %s, %s)""",
                (uid, username, real_name, email, age, major, user_type, status, created_at)
            )
            users.append({
                "id": uid, "username": username, "real_name": real_name,
                "major": major, "age": age, "user_type": user_type
            })

        # 确保管理员账号存在
        cur.execute(
            """INSERT IGNORE INTO user (username, password, real_name, email, age, major, user_type, status)
               VALUES ('admin', '123456', '系统管理员', 'admin@jxut.edu.cn', 30, '计算机科学与技术', '管理员', '正常')"""
        )
    conn.commit()
    print(f"[INFO] {USER_COUNT} 个用户数据生成完成")
    return users


def generate_subjects(conn):
    """插入扩展科目数据"""
    print(f"[INFO] 正在插入 {len(SUBJECTS)} 个科目...")
    subject_ids = []
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM subject")
        max_id = cur.fetchone()[0]
        for i, subj in enumerate(SUBJECTS, 1):
            sid = max_id + i
            cur.execute(
                """INSERT INTO subject (id, name, creator, description, credit, hours, category, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                (sid, subj["name"], subj["creator"], subj["description"],
                 subj["credit"], subj["hours"], subj["category"])
            )
            subject_ids.append(sid)
    conn.commit()
    print(f"[INFO] {len(SUBJECTS)} 个科目插入完成")
    return subject_ids


def generate_study_records(conn, users, subject_ids):
    """生成5000条学习记录"""
    print(f"[INFO] 正在生成 {STUDY_RECORD_COUNT} 条学习记录...")
    study_names = [
        "课件_第{}章", "实验指导_实验{}", "课后习题{}", "课程笔记_{}",
        "项目源码_{}", "学习总结_{}", "参考资料_{}", "练习题_{}",
        "课程设计_{}", "复习大纲_{}"
    ]
    with conn.cursor() as cur:
        for i in range(STUDY_RECORD_COUNT):
            user = random.choice(users)
            subject_id = random.choice(subject_ids)
            # 课件名称
            base_name = random.choice(study_names)
            ch = random.randint(1, 12)
            name = base_name.format(ch)
            if i < 50:
                name = f"期末复习资料_{random.choice(SUBJECTS)['name']}"

            upload_date = fake.date_between(start_date="-1y", end_date="today")
            duration = random.choice([30, 45, 60, 90, 120])
            download_count = random.randint(0, 200)
            file_size = random.randint(512, 10240)
            description = f"{user['real_name']}上传的{name}课件"

            cur.execute(
                """INSERT INTO study (title, creator, upload_date, subject_id, duration,
                                      download_count, file_size, description, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (name, user["username"], upload_date, subject_id,
                 duration, download_count, file_size, description)
            )
            if (i + 1) % 1000 == 0:
                conn.commit()
                print(f"  ... 已生成 {i + 1}/{STUDY_RECORD_COUNT} 条记录")
        conn.commit()
    print(f"[INFO] {STUDY_RECORD_COUNT} 条学习记录生成完成")


def generate_behavior_features(conn, users):
    """填充用户行为特征数据（用于聚类分析）"""
    print(f"[INFO] 正在计算并填充用户行为特征表...")
    with conn.cursor() as cur:
        # 清空重建
        cur.execute("DELETE FROM user_behavior_feature")

        # 从 study 表聚合计算，插入到 user_behavior_feature
        # 表结构: id(auto), user_id, total_study_count, total_study_hours, avg_study_duration,
        #          study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label, created_at
        cur.execute("""
            INSERT INTO user_behavior_feature 
                (user_id, total_study_count, total_study_hours, avg_study_duration,
                 study_days, review_count, subject_count, max_consecutive_days, avg_score, cluster_label, created_at)
            SELECT
                u.id,
                COUNT(st.id),
                COALESCE(SUM(st.duration), 0),
                ROUN