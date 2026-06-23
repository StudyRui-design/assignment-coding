-- ============================================================
-- Recruitment Role Data Analytics - 数据库初始化
-- ============================================================

CREATE DATABASE IF NOT EXISTS recruitment_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE recruitment_db;

DROP TABLE IF EXISTS t_recruitment_info;

CREATE TABLE t_recruitment_info (
    id              INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    job_name        VARCHAR(255)    COMMENT '岗位名称',
    job_area        VARCHAR(255)    COMMENT '工作区域',
    salary_lower    INT             COMMENT '薪资下限(K)',
    salary_high     INT             COMMENT '薪资上限(K)',
    com_name        VARCHAR(255)    COMMENT '公司名称',
    com_type        VARCHAR(50)     COMMENT '企业类型',
    com_size        VARCHAR(50)     COMMENT '企业规模',
    work_year       VARCHAR(50)     COMMENT '工作经验',
    education       VARCHAR(50)     COMMENT '学历要求',
    job_benefits    TEXT            COMMENT '岗位福利',
    city            VARCHAR(50)     COMMENT '城市',
    district        VARCHAR(50)     COMMENT '区域',
    street          VARCHAR(100)    COMMENT '街道',
    -- 常用查询索引
    INDEX idx_city (city),
    INDEX idx_salary_lower (salary_lower),
    INDEX idx_salary_high (salary_high),
    INDEX idx_com_type (com_type),
    INDEX idx_com_size (com_size),
    INDEX idx_work_year (work_year),
    INDEX idx_education (education)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recruitment岗位信息表';
