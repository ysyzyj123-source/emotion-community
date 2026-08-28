-- 大学生情感互助系统 数据库初始化脚本
-- 对应开题报告 6.3 / 6.4 节，共 14 张表
-- 使用：mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS emotion_community
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE emotion_community;

-- 板块表
CREATE TABLE IF NOT EXISTS category (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(32) NOT NULL UNIQUE,
  description VARCHAR(255),
  sort       INT DEFAULT 0,
  status     INT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 普通用户表
CREATE TABLE IF NOT EXISTS user (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  student_no VARCHAR(32) NOT NULL UNIQUE,
  nickname   VARCHAR(64) NOT NULL,
  password   VARCHAR(255) NOT NULL,
  avatar     VARCHAR(255),
  anonymous  TINYINT(1) DEFAULT 1,
  points     INT DEFAULT 0,
  level      INT DEFAULT 1,
  status     INT DEFAULT 1,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 心理辅导老师表
CREATE TABLE IF NOT EXISTS teacher (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  job_no     VARCHAR(32) NOT NULL UNIQUE,
  name       VARCHAR(64) NOT NULL,
  password   VARCHAR(255) NOT NULL,
  role       VARCHAR(16) DEFAULT 'teacher',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统管理员表
CREATE TABLE IF NOT EXISTS admin (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(64) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 帖子表
CREATE TABLE IF NOT EXISTS post (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  user_id    INT NOT NULL,
  title      VARCHAR(200) NOT NULL,
  content    TEXT NOT NULL,
  sentiment_label VARCHAR(16),
  emergency  VARCHAR(16),
  category_label VARCHAR(32),
  status     INT DEFAULT 1,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES category(id),
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 回复表
CREATE TABLE IF NOT EXISTS reply (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  post_id    INT NOT NULL,
  user_id    INT NOT NULL,
  content    TEXT NOT NULL,
  result     VARCHAR(16),
  adopted    TINYINT(1) DEFAULT 0,
  like_count INT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES post(id),
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 收藏表
CREATE TABLE IF NOT EXISTS collect (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  post_id    INT NOT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_collect (user_id, post_id),
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (post_id) REFERENCES post(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 情感分析结果表
CREATE TABLE IF NOT EXISTS sentiment_result (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  target_id  INT NOT NULL,
  target_type VARCHAR(16) NOT NULL,
  sentiment  VARCHAR(16),
  emergency  VARCHAR(16),
  score      FLOAT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 话题分析结果表
CREATE TABLE IF NOT EXISTS topic_result (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  post_id    INT NOT NULL,
  topic_label VARCHAR(32),
  category_id INT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES post(id),
  FOREIGN KEY (category_id) REFERENCES category(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 积分记录表
CREATE TABLE IF NOT EXISTS point_record (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  `change`   INT NOT NULL,
  action     VARCHAR(32),
  remark     VARCHAR(255),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 举报表
CREATE TABLE IF NOT EXISTS report (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  target_type VARCHAR(16),
  target_id  INT NOT NULL,
  reason     VARCHAR(255),
  status     INT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 反馈表
CREATE TABLE IF NOT EXISTS feedback (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  type       VARCHAR(16),
  content    TEXT,
  status     INT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 通知表
CREATE TABLE IF NOT EXISTS notice (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  content    VARCHAR(500),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 预警记录表
CREATE TABLE IF NOT EXISTS warning (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  post_id    INT NOT NULL,
  emergency  VARCHAR(16),
  status     INT DEFAULT 0,
  handler    INT,
  handle_note TEXT,
  handle_time DATETIME,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES post(id),
  FOREIGN KEY (handler) REFERENCES teacher(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
