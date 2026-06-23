-- ============================================
-- 邓睿的大数据应用课件管理系统 - 数据库初始化脚本
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS test DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE test;

-- 用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码（SHA-256加密）',
    `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
    `gender` VARCHAR(4) DEFAULT NULL COMMENT '性别',
    `birthday` DATE DEFAULT NULL COMMENT '出生日期',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '电话',
    `address` VARCHAR(200) DEFAULT NULL COMMENT '地址',
    `user_type` VARCHAR(20) DEFAULT '学员' COMMENT '用户类别：学员/老师/管理员',
    `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 科目表
CREATE TABLE IF NOT EXISTS `subject` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '科目名称',
    `creator` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
    `status` VARCHAR(10) DEFAULT '正常' COMMENT '状态：正常/禁用',
    `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科目表';

-- 课件表
CREATE TABLE IF NOT EXISTS `study` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL COMMENT '课件资源名',
    `subject_name` VARCHAR(100) DEFAULT NULL COMMENT '所属科目',
    `description` TEXT COMMENT '课件简介',
    `detail` TEXT COMMENT '课件详情',
    `file_path` VARCHAR(500) DEFAULT NULL COMMENT '课件附件路径',
    `creator` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
    `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `user_id` INT DEFAULT NULL COMMENT '学习用户ID（关联user表）',
    `duration` INT DEFAULT 0 COMMENT '学习时长（分钟）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课件表';

-- 用户行为特征表（Spark大数据分析用）
CREATE TABLE IF NOT EXISTS `user_behavior_feature` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `total_study_count` INT DEFAULT 0 COMMENT '总学习次数',
    `total_duration` BIGINT DEFAULT 0 COMMENT '总学习时长（分钟）',
    `activity_ratio` DOUBLE DEFAULT 0 COMMENT '活跃度比例',
    `last_study_time` TIMESTAMP NULL COMMENT '最后学习时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户行为特征表';

-- 用户科目评分表（Spark大数据分析用）
CREATE TABLE IF NOT EXISTS `user_subject_rating` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `subject_id` INT NOT NULL COMMENT '科目ID',
    `rating` DOUBLE DEFAULT 0 COMMENT '评分（0-5）',
    `comment` TEXT COMMENT '评语',
    `rate_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subject`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户科目评分表';

-- 插入默认管理员用户（密码: admin，明文存储兼容模式）
INSERT INTO `user` (username, password, real_name, user_type) VALUES
('admin', 'admin', '管理员', '管理员'),
('test', '123456', '测试用户', '学员');

-- 插入初始科目数据
INSERT INTO `subject` (name, creator, status) VALUES
('HTML', 'admin', '正常'),
('JavaScript', 'admin', '正常'),
('Java', 'admin', '正常'),
('Python', 'admin', '正常'),
('数据库技术', 'admin', '正常');
