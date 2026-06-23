CREATE DATABASE IF NOT EXISTS test DEFAULT CHARACTER SET utf8mb4;
USE test;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `study`;
DROP TABLE IF EXISTS `subject`;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `user_behavior_feature`;
DROP TABLE IF EXISTS `user_subject_rating`;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(64) NOT NULL,
    `real_name` VARCHAR(50),
    `gender` VARCHAR(4) DEFAULT '男',
    `birth` VARCHAR(20),
    `phone` VARCHAR(20),
    `address` VARCHAR(200),
    `user_type` VARCHAR(10) DEFAULT '学员',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `subject` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `creator` VARCHAR(50),
    `status` VARCHAR(20) DEFAULT '启用',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `study` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `subject_id` INT,
    `subject_name` VARCHAR(100),
    `summary` VARCHAR(500),
    `content` TEXT,
    `file_src` VARCHAR(500),
    `creator` VARCHAR(50),
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`subject_id`) REFERENCES `subject`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
