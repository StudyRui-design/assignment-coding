-- ============================================
-- 大数据技术开发实训 - 课件管理系统 数据库初始化脚本
-- 使用前修改 DbUtil.java 中的数据库连接信息
-- ============================================

CREATE DATABASE IF NOT EXISTS test DEFAULT CHARACTER SET utf8mb4;
USE test;

-- 1. 用户表
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名/账号',
    `password` VARCHAR(64) NOT NULL COMMENT '密码(MD5加密)',
    `real_name` VARCHAR(50) COMMENT '真实姓名',
    `gender` VARCHAR(4) DEFAULT '男' COMMENT '性别',
    `birth` VARCHAR(20) COMMENT '出生日期',
    `phone` VARCHAR(20) COMMENT '电话',
    `address` VARCHAR(200) COMMENT '地址',
    `user_type` VARCHAR(10) DEFAULT '学员' COMMENT '用户类型: 学员/老师/管理员',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 科目表
DROP TABLE IF EXISTS `subject`;
CREATE TABLE `subject` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '科目名称',
    `creator` VARCHAR(50) COMMENT '创建人',
    `status` VARCHAR(20) DEFAULT '启用' COMMENT '状态',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 课件(学习资源)表
DROP TABLE IF EXISTS `study`;
CREATE TABLE `study` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL COMMENT '课件资源名',
    `subject_id` INT COMMENT '所属科目ID',
    `subject_name` VARCHAR(100) COMMENT '所属科目名',
    `summary` VARCHAR(500) COMMENT '课件简介',
    `content` TEXT COMMENT '课件详情(HTML内容)',
    `file_src` VARCHAR(500) COMMENT '课件附件路径',
    `creator` VARCHAR(50) COMMENT '上传用户',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传日期',
    FOREIGN KEY (`subject_id`) REFERENCES `subject`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入初始化数据
INSERT INTO `user` (username, password, real_name, gender, birth, phone, address, user_type) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', '管理员', '男', '1990-01-01', '13800000000', '北京', '管理员'),
('teacher01', 'e10adc3949ba59abbe56e057f20f883e', '陈晨', '男', '1992-05-15', '15918230478', '上海', '老师'),
('student01', 'e10adc3949ba59abbe56e057f20f883e', '韩露', '女', '1998-02-01', '15918230478', '深圳', '学员');

INSERT INTO `subject` (name, creator, status) VALUES
('HTML', 'admin', '启用'),
('JavaScript', 'admin', '启用'),
('Java', 'admin', '启用'),
('Python', 'admin', '启用'),
('大数据技术', 'admin', '启用');

INSERT INTO `study` (title, subject_id, subject_name, summary, content, file_src, creator) VALUES
('HTML新功能讲解', 1, 'HTML', '增加了播放视频功能', '<h3>HTML5视频功能</h3><p>支持video标签，可直接播放视频</p>', 'ziliao/Wildlife.wmv', 'admin'),
('JavaScript DOM操作', 2, 'JavaScript', '图片轮播功能实现', '<h3>DOM操作详解</h3><p>通过JavaScript操作DOM实现动态效果</p>', '', 'teacher01'),
('Java基础语法', 3, 'Java', 'Java入门教程', '<h3>Java基础</h3><p>变量、循环、条件判断等基础内容</p>', '', 'admin');
