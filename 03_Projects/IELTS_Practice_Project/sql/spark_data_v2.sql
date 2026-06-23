USE test;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS user_behavior_feature;
DROP TABLE IF EXISTS user_subject_rating;

CREATE TABLE user_behavior_feature (
    user_id INT PRIMARY KEY,
    total_study_count INT DEFAULT 0,
    total_study_hours FLOAT DEFAULT 0,
    avg_study_duration FLOAT DEFAULT 0,
    study_days INT DEFAULT 5,
    review_count INT DEFAULT 0,
    subject_count INT DEFAULT 1,
    max_consecutive_days INT DEFAULT 1,
    avg_score FLOAT DEFAULT 4.0,
    cluster_label VARCHAR(20) DEFAULT 'new'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO user_behavior_feature (user_id, total_study_count, study_days, subject_count, cluster_label)
SELECT id,
       FLOOR(3 + RAND() * 20),
       FLOOR(2 + RAND() * 15),
       FLOOR(1 + RAND() * 5),
       ELT(FLOOR(1 + RAND() * 4), 'active', 'normal', 'quiet', 'new')
FROM user;

CREATE TABLE user_subject_rating (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject_id INT NOT NULL,
    rating FLOAT DEFAULT 3.5,
    interaction_count INT DEFAULT 1,
    comment VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_subject (user_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO user_subject_rating (user_id, subject_id, rating, interaction_count, comment)
SELECT
    u.id AS user_id,
    s.id AS subject_id,
    ROUND(3 + RAND() * 2, 1) AS rating,
    FLOOR(1 + RAND() * 10) AS interaction_count,
    ELT(FLOOR(1+RAND()*5), 'good course', 'very helpful', 'clear explanation', 'great content', 'recommended')
FROM user u CROSS JOIN subject s
WHERE RAND() < 0.6;

UPDATE study SET download_count = FLOOR(10 + RAND() * 100) WHERE download_count IS NULL OR download_count = 0;
UPDATE study SET duration = FLOOR(20 + RAND() * 80) WHERE duration IS NULL OR duration = 0;

SET FOREIGN_KEY_CHECKS = 1;
