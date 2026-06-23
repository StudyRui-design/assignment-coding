USE test;
ALTER TABLE study ADD COLUMN download_count INT DEFAULT 0;
ALTER TABLE study ADD COLUMN duration INT DEFAULT 45;
UPDATE study SET download_count = FLOOR(10 + RAND() * 100), duration = FLOOR(20 + RAND() * 80);
