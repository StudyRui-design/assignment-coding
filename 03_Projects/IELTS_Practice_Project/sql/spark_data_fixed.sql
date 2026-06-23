USE test;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. 为 study 表添加缺少的字段
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `download_count` INT DEFAULT 0 COMMENT '下载次数';
ALTER TABLE `study` ADD COLUMN IF NOT EXISTS `duration` INT DEFAULT 45 COMMENT '学习时长分钟';

-- 2. 创建用户行为特征表
DROP TABLE IF EXISTS `user_behavior_feature`;
CREATE TABLE `user_behavior_feature` (
    `user_id` INT PRIMARY KEY COMMENT '用户ID',
    `total_study_count` INT DEFAULT 0,
    `total_study_hours` FLOAT DEFAULT 0,
    `avg_study_duration` FLOAT DEFAULT 0,
    `study_days` INT DEFAULT 0,
    `review_count` INT DEFAULT 0,
    `subject_count` INT DEFAULT 0,
    `max_consecutive_days` INT DEFAULT 0,
    `avg_score` FLOAT DEFAULT 0,
    `cluster_label` VARCHAR(20) DEFAULT '新手用户'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `user_behavior_feature` (`user_id`) SELECT id FROM `user`;

-- 3. 创建用户评分表
DROP TABLE IF EXISTS `user_subject_rating`;
CREATE TABLE `user_subject_rating` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `rating` FLOAT DEFAULT 3.5 COMMENT '评分(1-5)',
    `interaction_count` INT DEFAULT 1,
    `comment` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_subject` (`user_id`, `subject_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 插入扩展科目数据
INSERT IGNORE INTO `subject` (`name`, `creator`, `status`) VALUES
('Java程序设计', 'admin', '启用'),
('Python数据分析', 'admin', '启用'),
('数据结构', 'admin', '启用'),
('操作系统', 'admin', '启用'),
('计算机网络', 'admin', '启用'),
('数据库原理', 'admin', '启用'),
('机器学习基础', 'admin', '启用'),
('深度学习实战', 'admin', '启用'),
('Web前端开发', 'admin', '启用'),
('算法设计与分析', 'admin', '启用');

SET FOREIGN_KEY_CHECKS = 1;
