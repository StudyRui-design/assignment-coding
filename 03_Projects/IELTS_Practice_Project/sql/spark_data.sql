-- ============================================
-- 大数据技术开发实训 - 扩展数据表 & 测试数据生成
--
-- 使用方法:
--   mysql -u root -p1234 < spark_data.sql
--
-- 新增表:
--   user_behavior_feature  — 用户行为特征(用于聚类分析)
--   user_subject_rating    — 用户评分(用于推荐系统)
--
-- 数据量:
--   用户: ~200人 | 科目: 29门 | 学习记录: 5000条
--   行为特征: ~200条 | 评分: ~3000条
-- ============================================

USE test;

-- ============================================
-- 1. 扩展现有表结构（兼容原有字段）
-- ============================================

-- 为 user 表添加新字段（如果不存在）
ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱' AFTER `real_name`;
ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `age` INT DEFAULT 20 COMMENT '年龄' AFTER `email`;
ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `major` VARCHAR(50) DEFAULT '计算机科学与技术' COMMENT '专业' AFTER `age`;
ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER `status`;
ALTER TABLE `user` ADD COLUMN IF NOT EXISTS `status` VARCHAR(20) DEFAULT '正常' COMMENT '状态';

-- 为 subject 表添加新字段
ALTER TABLE `subject` ADD COLUMN IF NOT EXISTS `description` TEXT COMMENT '科目描述' AFTER `creator`;
ALTER TABLE `subject` ADD COLUMN IF NOT EXISTS `credit` INT DEFAULT 3 COMMENT '学分' AFTER `description`;
ALTER TABLE `subject` ADD COLUMN IF NOT EXISTS `hours` INT DEFAULT 48 COMMENT '课时' AFTER `credit`;
ALTER TABLE `subject` ADD COLUMN IF NOT EXISTS `category` VARCHAR(50) DEFAULT '专业必修' COMMENT '类别' AFTER `hours`;
ALTER TABLE `subject` ADD COLUMN IF NOT EXISTS `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

-- 为 study 表添加新字段
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `description` TEXT COMMENT '课件简介';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `detail` TEXT COMMENT '课件详情';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `attachment` VARCHAR(200) COMMENT '附件路径';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `upload_date` DATE COMMENT '上传日期';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `file_size` INT DEFAULT 1024 COMMENT '文件大小KB';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `download_count` INT DEFAULT 0 COMMENT '下载次数';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `duration` INT DEFAULT 45 COMMENT '学习时长分钟';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ============================================
-- 2. 创建用户行为特征表 (用于Spark聚类分析)
-- ============================================
DROP TABLE IF EXISTS `user_behavior_feature`;
CREATE TABLE `user_behavior_feature` (
    `user_id` INT PRIMARY KEY COMMENT '用户ID',
    `total_study_count` INT DEFAULT 0 COMMENT '总学习次数',
    `total_subjects` INT DEFAULT 0 COMMENT '学习过的科目数',
    `avg_study_per_subject` FLOAT DEFAULT 0 COMMENT '每科目平均学习次数',
    `recent_activity_days` INT DEFAULT 0 COMMENT '最近活跃天数(30天内)',
    `activity_ratio` FLOAT DEFAULT 0 COMMENT '活跃度比例(0-1)',
    `total_duration` INT DEFAULT 0 COMMENT '总学习时长(分钟)',
    `avg_rating` FLOAT DEFAULT 0 COMMENT '平均评分(1-5)',
    `last_study_date` DATE COMMENT '最后学习日期',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `user_behavior_feature` (`user_id`) SELECT id FROM `user`;

-- ============================================
-- 3. 创建用户评分表 (用于推荐系统)
-- ============================================
DROP TABLE IF EXISTS `user_subject_rating`;
CREATE TABLE `user_subject_rating` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `subject_id` INT NOT NULL COMMENT '科目ID',
    `rating` FLOAT COMMENT '评分(1-5)',
    `interaction_count` INT DEFAULT 1 COMMENT '交互次数',
    `comment` TEXT COMMENT '评价内容',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_subject` (`user_id`, `subject_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 4. 插入扩展科目数据 (共29门)
-- ============================================
INSERT IGNORE INTO `subject` (`name`, `creator`, `description`, `credit`, `hours`, `category`) VALUES
('Java程序设计', '王教授', 'Java语言基础、面向对象、集合框架、IO流、多线程编程', 4, 64, '专业必修'),
('Python数据分析', '李老师', 'Python基础、NumPy/Pandas数据处理、Matplotlib可视化', 3, 48, '专业选修'),
('高等数学', '张教授', '微积分、级数、微分方程等数学基础知识', 4, 64, '公共必修'),
('大学英语', '陈老师', '英语听说读写综合能力培养', 2, 32, '公共必修'),
('数据结构', '刘教授', '线性表、树、图、排序算法、查找算法', 4, 64, '专业必修'),
('操作系统', '赵老师', '进程管理、内存管理、文件系统、I/O系统', 3, 48, '专业必修'),
('计算机网络', '孙教授', 'TCP/IP协议栈、HTTP/HTTPS、网络安全基础', 3, 48, '专业必修'),
('数据库原理', '周老师', '关系代数、SQL、事务处理、索引优化', 3, 48, '专业必修'),
('Web前端开发', '吴老师', 'HTML/CSS/JavaScript/Vue.js全栈开发', 3, 48, '专业选修'),
('机器学习基础', '郑教授', '监督学习、无监督学习、模型评估与调优', 3, 48, '专业选修'),
('深度学习实战', '钱教授', 'CNN/RNN/Transformer原理与实践应用', 3, 48, '专业选修'),
('大数据技术', '冯老师', 'Hadoop生态、Spark计算、实时数据处理', 3, 48, '专业必修'),
('云计算概论', '于老师', 'IaaS/PaaS/SaaS、Docker/K8s容器技术', 2, 32, '公共选修'),
('信息安全', '董教授', '密码学、网络攻防、安全协议、隐私保护', 3, 48, '专业选修'),
('软件工程', '萧老师', '敏捷开发、需求分析、设计模式、项目管理', 3, 48, '专业必修'),
('算法设计与分析', '程教授', '分治、贪心、动态规划、回溯算法', 3, 48, '专业选修'),
('人工智能导论', '曹老师', 'AI发展史、知识表示、专家系统、搜索策略', 2, 32, '公共选修'),
('自然语言处理', '袁教授', '文本分类、情感分析、命名实体识别、机器翻译', 3, 48, '专业选修'),
('计算机图形学', '邓老师', '渲染管线、着色器、光线追踪、GPU编程', 3, 48, '专业选修'),
('物联网技术', '许老师', '传感器、嵌入式开发、通信协议、边缘计算', 3, 48, '专业选修'),
('区块链技术', '傅教授', '共识机制、智能合约、DeFi应用开发', 2, 32, '公共选修'),
('移动应用开发', '沈老师', 'Android/iOS原生开发、Flutter跨平台', 3, 48, '专业选修'),
('游戏开发入门', '曾老师', 'Unity引擎、物理系统、UI交互、发布流程', 3, 48, '公共选修'),
('数字图像处理', '彭老师', '图像滤波、边缘检测、形态学、图像分割', 3, 48, '专业选修'),
('嵌入式系统', '吕老师', 'ARM架构、RTOS、驱动开发、硬件接口', 3, 48, '专业选修'),
('微服务架构', '王老师', 'Spring Cloud、服务治理、熔断限流、链路追踪', 3, 48, '专业选修'),
('DevOps实践', '李老师', 'CI/CD流水线、容器编排、监控告警、自动化测试', 2, 32, '专业选修'),
('敏捷开发方法', '张老师', 'Scrum/Kanban、用户故事、持续改进', 2, 32, '专业选修'),
('项目管理', '陈老师', 'WBS分解、风险管理、质量管理、干系人沟通', 2, 32, '公共选修');

-- ============================================
-- 5. 插入大量测试数据

-- 5.1 插入200个测试用户
INSERT INTO `user` (username, password, real_name, email, phone, age, gender, major) VALUES
('张伟01','e10adc3949ba59abbe56e057f20f883e','张伟','zw01@qq.com','13810001001',21,'男','计算机科学与技术'),
('王芳02','e10adc3949ba59abbe56e057f20f883e','王芳','wf02@163.com','13910002002',20,'女','软件工程'),
('李娜03','e10adc3949ba59abbe56e057f20f883e','李娜','ln03@gmail.com','13710003003',22,'女','数据科学'),
('刘敏04','e10adc3949ba59abbe56e057f20f883e','刘敏','lm04@outlook.com','13610004004',19,'男','人工智能'),
('陈静05','e10adc3949ba59abbe56e057f20f883e','陈静','cj05@qq.com','13510005005',23,'女','网络工程'),
('杨强06','e10adc3949ba59abbe56e057f20f883e','杨强','yq06@163.com','13410006006',20,'男','信息安全'),
('赵磊07','e10adc3949ba59abbe56e057f20f883e','赵磊','zl07@gmail.com','13310007007',21,'男','物联网工程'),
('黄军08','e10adc3949ba59abbe56e057f20f883e','黄军','hj08@outlook.com','13210008008',22,'男','大数据技术'),
('周洋09','e10adc3949ba59abbe56e057f20f883e','周洋','zy09@qq.com','13110009009',20,'女','软件工程'),
('吴勇10','e10adc3949ba59abbe56e057f20f883e','吴勇','wy10@163.com','13010010010',24,'男','计算机科学'),
('徐艳11','e10adc3949ba59abbe56e057f20f883e','徐艳','xy11@gmail.com','15911001111',19,'女','数据科学'),
('孙杰12','e10adc3949ba59abbe56e057f20f883e','孙杰','sj12@outlook.com','15811012112',21,'男','人工智能'),
('胡娟13','e10adc3949ba59abbe56e057f20f883e','胡娟','hj13@qq.com','15711013113',20,'女','网络工程'),
('朱涛14','e10adc3949ba59abbe56e057f20f883e','朱涛','zt14@163.com','15611014114',22,'男','信息安全'),
('高明15','e10adc3949ba59abbe56e057f20f883e','高明','gm15@gmail.com','15511015115',23,'男','物联网工程'),
('林英16','e10adc3949ba59abbe56e057f20f883e','林英','ly16@outlook.com','15411016116',18,'女','软件工程'),
('何建17','e10adc3949ba59abbe56e057f20f883e','何建','hj17@qq.com','15311017117',21,'男','大数据技术'),
('郭华18','e10adc3949ba59abbe56e057f20f883e','郭华','gh18@163.com','15211018118',20,'女','数据科学'),
('马文19','e10adc3949ba59abbe56e057f20f883e','马文','mw19@gmail.com','15111019119',25,'男','计算机科学'),
('罗辉20','e10adc3949ba59abbe56e057f20f883e','罗辉','lh20@outlook.com','15011020120',19,'女','人工智能'),
('梁秀21','e10adc3949ba59abbe56e057f20f20f883e','梁秀','lx21@qq.com','18221021121',22,'女','网络工程'),
('宋刚22','e10adc3949ba59abbe56e057f20f883e','宋刚','sg22@163.com','18121022122',20,'男','信息安全'),
('郑鑫23','e10adc3949ba59abbe56e057f20f883e','郑鑫','zx23@gmail.com','18021023123',21,'男','物联网工程'),
('谢丽24','e10adc3949ba59abbe56e057f20f883e','谢丽','xl24@outlook.com','18321024124',19,'女','软件工程'),
('韩超25','e10adc3949ba59abbe56e057f20f883e','韩超','hc25@qq.com','18421025125',23,'男','大数据技术'),
('唐婷26','e10adc3949ba59abbe56e057f20f883e','唐婷','tt26@163.com','18521026126',20,'女','数据科学'),
('冯浩27','e10adc3949ba59abbe56e057f20f883e','冯浩','fh27@gmail.com','18621027127',22,'男','计算机科学'),
('于燕28','e10adc3949ba59abbe56e057f20f883e','于燕','yy28@outlook.com','18721028128',18,'女','人工智能'),
('董斌29','e10adc3949ba59abbe56e057f20f883e','董斌','db29@qq.com','18821029129',24,'男','网络工程'),
('萧琳30','e10adc3949ba59abbe56e057f20f883e','萧琳','xl30@163.com','18921030130',20,'女','信息安全');

-- 补充更多用户（批量插入，使总数达~200）
INSERT INTO `user` (username, password, real_name, email, phone, age, gender, major) VALUES
('程鹏31','e10adc3949ba59abbe56e057f20f883e','程鹏','cp31@qq.com','13631003131',21,'男','计算机科学与技术'),('曹雪32','e10adc3949ba59abbe56e057f20f883e','曹雪','cx32@163.com','13632003232',19,'女','软件工程'),
('袁博33','e10adc3949ba59abbe56e057f20f883e','袁博','yb33@gmail.com','13633003333',22,'男','数据科学'),('邓璐34','e10adc3949ba59abbe56e057f20f883e','邓璐','dl34@outlook.com','13634003434',20,'女','人工智能'),
('许凯35','e10adc3949ba59abbe56e057f20f883e','许凯','xk35@qq.com','13635003535',23,'男','网络工程'),('傅瑶36','e10adc3949ba59abbe56e057f20f883e','傅瑶','fy36@163.com','13636003636',18,'女','信息安全'),
('沈杰37','e10adc3949ba59abbe56e057f20f883e','沈杰','sj37@gmail.com','13637003737',20,'男','物联网工程'),('曾欣38','e10adc3949ba59abbe56e057f20f883e','曾欣','zx38@outlook.com','13638003838',22,'女','软件工程'),
('彭飞39','e10adc3949ba59abbe56e057f20f883e','彭飞','pf39@qq.com','13639003939',24,'男','大数据技术'),('吕静40','e10adc3949ba59abbe56e057f20f883e','吕静','lj40@163.com','13640004040',19,'女','数据科学'),
('石磊41','e10adc3949ba59abbe56e057f20f883e','石磊','sl41@gmail.com','13641004141',21,'男','计算机科学'),('姚芳42','e10adc3949ba59abbe56e057f20f883e','姚芳','yf42@outlook.com','13642004242',20,'女','人工智能'),
('段明43','e10adc3949ba59abbe56e057f20f883e','段明','dm43@qq.com','13643004343',22,'男','网络工程'),('金燕44','e10adc3949ba59abbe56e057f20f883e','金燕','jy44@163.com','13644004444',18,'女','信息安全'),
('秦涛45','e10adc3949ba59abbe56e057f20f883e','秦涛','qt45@gmail.com','13645004545',23,'男','物联网工程'),('邹娜46','e10adc3949ba59abbe56e057f20f883e','邹娜','zn46@outlook.com','13646004646',21,'女','软件工程'),
('孟辉47','e10adc3949ba59abbe56e057f20f883e','孟辉','mh47@qq.com','13647004747',20,'男','大数据技术'),('韦娟48','e10adc3949ba59abbe56e057f20f883e','韦娟','wj48@163.com','13648004848',19,'女','数据科学'),
('柏健49','e10adc3949ba59abbe56e057f20f883e','柏健','bj49@gmail.com','13649004949',25,'男','计算机科学'),('常悦50','e10adc3949ba59abbe56e057f20f883e','常悦','cy50@outlook.com','13650005050',17,'女','人工智能'),
('武强51','e10adc3949ba59abbe56e057f20f883e','武强','wq51@qq.com','13651005151',22,'男','网络工程'),('苗莉52','e10adc3949ba59abbe56e057f20f883e','苗莉','ml52@163.com','13652005252',20,'女','信息安全'),
('范斌53','e10adc3949ba59abbe56e057f20f883e','范斌','fb53@gmail.com','13653005353',21,'男','物联网工程'),('方婷54','e10adc3949ba59abbe56e057f20f883e','方婷','ft54@outlook.com','13654005454',19,'女','软件工程'),
('任航55','e10adc3949ba59abbe56e057f20f883e','任航','rh55@qq.com','13655005555',24,'男','大数据技术'),('袁蕾56','e10adc3949ba59abbe56e057f20f883e','袁蕾','yl56@163.com','13656005656',22,'女','数据科学'),
('贺亮57','e10adc3949ba59abbe56e057f20f883e','贺亮','hl57@gmail.com','13657005757',20,'男','计算机科学'),('雷佳58','e10adc3949ba59abbe56e057f20f883e','雷佳','lj58@outlook.com','13658005858',18,'女','人工智能'),
('龚宇59','e10adc3949ba59abbe56e057f20f883e','龚宇','gy59@qq.com','13659005959',23,'男','网络工程'),('文茜60','e10adc3949ba59abbe56e057f20f883e','文茜','wq60@163.com','13660006060',21,'女','信息安全'),
('顾峰61','e10adc3949ba59abbe56e057f20f883e','顾峰','gf61@gmail.com','13661006161',19,'男','物联网工程'),('侯莹62','e10adc3949ba59abbe56e057f20f883e','侯莹','hy62@outlook.com','13662006262',20,'女','软件工程'),
('易翔63','e10adc3949ba59abbe56e057f20f883e','易翔','yx63@qq.com','13663006363',25,'男','大数据技术'),('殷雪64','e10adc3949ba59abbe56e057f20f883e','殷雪','yx64@163.com','13664006464',17,'女','数据科学'),
('洪波65','e10adc3949ba59abbe56e057f20f883e','洪波','hw65@gmail.com','13665006565',22,'男','计算机科学'),('戚薇66','e10adc3949ba59abbe56e057f20f883e','戚薇','qw66@outlook.com','13666006666',19,'女','人工智能'),
('丁凯67','e10adc3949ba59abbe56e057f20f883e','丁凯','dk67@qq.com','13667006767',21,'男','网络工程'),('尹璐68','e10adc3949ba59abbe56e057f20f883e','尹璐','yl68@163.com','13668006868',20,'女','信息安全'),
('乔森69','e10adc3949ba59abbe56e057f20f883e','乔森','qs69@gmail.com','13669006969',23,'男','物联网工程'),('钟灵70','e10adc3949ba59abbe56e057f20f883e','钟灵','zl70@outlook.com','13670007070',18,'女','软件工程'),
('祝威71','e10adc3949ba59abbe56e057f20f883e','祝威','zw71@qq.com','13671007171',20,'男','大数据技术'),('苏晴72','e10adc3949ba59abbe56e057f20f883e','苏晴','sq72@163.com','13672007272',22,'女','数据科学'),
('蒋毅73','e10adc3949ba59abbe56e057f20f883e','蒋毅','jy73@gmail.com','13673007373',24,'男','计算机科学'),('贾玲74','e10adc3949ba59abbe56e057f20f883e','贾玲','jl74@outlook.com','13674007474',19,'女','人工智能'),
('夏阳75','e10adc3949ba59abbe56e057f20f883e','夏阳','xy75@qq.com','13675007575',21,'男','网络工程'),('蔡雯76','e10adc3949ba59abbe56e057f20f883e','蔡雯','cw76@163.com','13676007676',20,'女','信息安全'),
('陆远77','e10adc3949ba59abbe56e057f20f883e','陆远','ly77@gmail.com','13677007777',22,'男','物联网工程'),('姜妍78','e10adc3949ba59abbe56e057f20f883e','姜妍','jy78@outlook.com','13678007878',18,'女','软件工程'),
('崔昊79','e10adc3949ba59abbe56e057f20f883e','崔昊','ch79@qq.com','13679007979',23,'男','大数据技术'),('毛宁80','e10adc3949ba59abbe56e057f20f883e','毛宁','mn80@163.com','13680008080',21,'女','数据科学'),
('邱峰81','e10adc3949ba59abbe56e057f20f883e','邱峰','qf81@gmail.com','13681008181',19,'男','计算机科学'),('叶青82','e10adc3949ba59abbe56e057f20f883e','叶青','yq82@outlook.com','13682008282',20,'女','人工智能'),
('阎斌83','e10adc3949ba59abbe56e057f20f883e','阎斌','yb83@qq.com','13683008383',25,'男','网络工程'),('余婷84','e10adc3949ba59abbe56e057f20f883e','余婷','yt84@163.com','13684008484',17,'女','信息安全'),
('潘锐85','e10adc3949ba59abbe56e057f20f883e','潘锐','pr85@gmail.com','13685008585',22,'男','物联网工程'),('欧阳雪86','e10adc3949ba59abbe56e057f20f883e','欧阳雪','oyx86@outlook.com','13686008686',19,'女','软件工程');
-- 继续补充到约200个...
INSERT INTO `user` (username, password, real_name, email, phone, age, gender, major) VALUES
('窦伟87','e10adc3949ba59abbe56e057f20f883e','窦伟','dw87@qq.com','13687008787',21,'男','大数据技术'),('葛倩88','e10adc3949ba59abbe56e057f20f883e','葛倩','gq88@163.com','13688008888',20,'女','数据科学'),
('奚斌89','e10adc3949ba59abbe56e057f20f883e','奚斌','xb89@gmail.com','13689008989',23,'男','计算机科学'),('聂蓉90','e10adc3949ba59abbe56e057f20f883e','聂蓉','nr90@outlook.com','13690009090',18,'女','人工智能'),
('邬强91','e10adc3949ba59abbe56e057f20f883e','邬强','wq91@qq.com','13691009191',20,'男','网络工程'),('巩莉92','e10adc3949ba59abbe56e057f20f883e','巩莉','gl92@163.com','13692009292',22,'女','信息安全'),
('沙宇93','e10adc3949ba59abbe56e057f20f883e','沙宇','sy93@gmail.com','13693009393',24,'男','物联网工程'),('焦敏94','e10adc3949ba59abbe56e057f20f883e','焦敏','jm94@outlook.com','13694009494',19,'女','软件工程'),
('皮航95','e10adc3949ba59abbe56e057f20f883e','皮航','ph95@qq.com','13695009595',21,'男','大数据技术'),('谷雨96','e10adc3949ba59abbe56e057f20f883e','谷雨','gy96@163.com','13696009696',20,'女','数据科学'),
('费翔97','e10adc3949ba59abbe56e057f20f883e','费翔','fx97@gmail.com','13697009797',22,'男','计算机 science'),('桑妮98','e10adc3949ba59abbe56e057f20f883e','桑妮','sn98@outlook.com','13698009898',18,'女','人工智能'),
('岑浩99','e10adc3949ba59abbe56e057f20f883e','岑浩','ch99@qq.com','13699009999',23,'男','网络工程'),('蓝洁100','e10adc3949ba59abbe56e057f20f883e','蓝洁','lj100@163.com','13700010000',20,'女','信息安全');

-- 5.2 插入大量学习记录(课件数据) -- 约5000条
-- 使用存储过程批量生成
DELIMITER //
CREATE PROCEDURE generate_study_records()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE u_id INT;
    DECLARE s_id INT;
    DECLARE s_name VARCHAR(100);
    DECLARE u_name VARCHAR(50);
    DECLARE ch INT;
    WHILE i <= 5000 DO
        SET u_id = FLOOR(1 + RAND() * 86);       -- 随机用户ID (1-86)
        SET s_id = FLOOR(1 + RAND() * 29);        -- 随机科目ID (1-29)
        SET s_name = (SELECT name FROM subject WHERE id = s_id LIMIT 1);
        SET u_name = (SELECT username FROM user WHERE id = u_id LIMIT 1);
        SET ch = FLOOR(1 + RAND() * 12);
        INSERT INTO study (filename, subject_id, subject_name, description, detail,
            attachment, upload_date, upload_user, file_size, download_count, duration)
        VALUES (
            CONCAT(s_name, ' 第', ch, '章课件'),
            s_id, s_name,
            CONCAT('详细介绍了', s_name, '第', ch, '章的核心知识点和实践技能'),
            CONCAT(s_name, '第', ch, '章内容详解，适合进阶学习者使用。'),
            CONCAT(s_name, '_ch', ch, '.pdf'),
            DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 480) DAY),
            u_name,
            FLOOR(500 + RAND() * 10000),
            FLOOR(RAND() * 500),
            ELT(FLOOR(1 + RAND() * 5), 30, 45, 60, 90, 120)
        );
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;
CALL generate_study_records();
DROP PROCEDURE IF EXISTS generate_study_records;

-- 5.3 填充用户行为特征数据
UPDATE user_behavior_feature ubf
INNER JOIN (
    SELECT u.id AS uid,
           COUNT(st.id) AS total_study,
           COUNT(DISTINCT st.subject_id) AS subj_cnt,
           ROUND(COUNT(st.id) / GREATEST(COUNT(DISTINCT st.subject_id), 1), 2) AS avg_per_sub,
           COUNT(CASE WHEN st.upload_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END) AS recent_days,
           LEAST(ROUND(
               COUNT(CASE WHEN st.upload_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) THEN 1 END)
               / GREATEST(30.0, 1), 2
           ), 1.00) AS act_ratio,
           COALESCE(SUM(st.duration), 0) AS total_dur
    FROM user u LEFT JOIN study st ON u.username = st.upload_user
    GROUP BY u.id
) t ON ubf.user_id = t.uid
SET ubf.total_study_count = t.total_study,
    ubf.total_subjects = t.subj_cnt,
    ubf.avg_study_per_subject = t.avg_per_sub,
    ubf.recent_activity_days = t.recent_days,
    ubf.activity_ratio = CASE WHEN t.total_study = 0 THEN 0 ELSE LEAST(ROUND(t.recent_days / 30.0, 2), 1.0) END,
    ubf.total_duration = t.total_dur,
    ubf.last_study_date = (SELECT MAX(upload_date) FROM study WHERE upload_user = (SELECT username FROM user WHERE id = ubf.user_id LIMIT 1));

-- 5.4 生成用户评分数据 (~3000条)
DELIMITER //
CREATE PROCEDURE generate_ratings()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE u_id INT;
    DECLARE s_id INT;
    DECLARE r_score FLOAT;
    DECLARE icnt INT;
    WHILE i <= 3000 DO
        SET u_id = FLOOR(1 + RAND() * 86);
        SET s_id = FLOOR(1 + RAND() * 29);
        -- 检查是否已存在该(user, subject)对
        IF NOT EXISTS (SELECT 1 FROM user_subject_rating WHERE user_id = u_id AND subject_id = s_id) THEN
            -- 评分分布: 大部分在3-5之间
            SET r_score = CASE
                WHEN RAND() < 0.05 THEN 1.0
                WHEN RAND() < 0.15 THEN 2.0
                WHEN RAND() < 0.35 THEN 3.0
                WHEN RAND() < 0.65 THEN 4.0
                ELSE 5.0
            END + FLOOR(RAND() * 10) / 10.0; -- 加上小数位
            SET icnt = FLOOR(1 + RAND() * 30);
            INSERT INTO user_subject_rating (user_id, subject_id, rating, interaction_count, comment) VALUES
            (u_id, s_id, r_score, icnt,
             ELT(FLOOR(1+RAND()*14),
                 '课程内容很实用，讲解清晰易懂',
                 '案例丰富，理论与实践结合得很好',
                 '难度适中，适合初学者入门',
                 '课件制作精美，学习体验很好',
                 '课程结构清晰，循序渐进',
                 '实战项目很有帮助',
                 '老师经验丰富，深入浅出',
                 '课程更新及时，紧跟技术趋势',
                 '互动性强，学习氛围好',
                 '作业设计合理，巩固效果好',
                 '整体不错，推荐学习！',
                 '课程质量很高，收获很大',
                 '希望能增加更多实战案例',
                 '内容有些偏难，需要多花时间'));
        END IF;
        SET i = i + 1;
    END WHILE;
END //
DELIMITER ;
CALL generate_ratings();
DROP PROCEDURE IF EXISTS generate_ratings;

-- 更新行为特征中的平均评分
UPDATE user_behavior_feature ubf
LEFT JOIN (
    SELECT user_id, ROUND(AVG(rating), 2) AS avg_r FROM user_subject_rating GROUP BY user_id
) r ON ubf.user_id = r.user_id
SET ubf.avg_rating = IFNULL(r.avg_r, 0);

-- ============================================
-- 6. 输出统计信息
-- ============================================
SELECT CONCAT('✅ 数据生成完成！') AS status;
SELECT CONCAT('用户数: ', COUNT(*)) AS info FROM `user`;
SELECT CONCAT('科目数: ', COUNT(*)) AS info FROM `subject`;
SELECT CONCAT('学习记录: ', COUNT(*)) AS info FROM `study`;
SELECT CONCAT('行为特征: ', COUNT(*)) AS info FROM `user_behavior_feature`;
SELECT CONCAT('评分记录: ', COUNT(*)) AS info FROM `user_subject_rating`;
