-- 初始数据：四大板块 + 演示账号（密码占位，需按实际加密填充）
USE emotion_community;

INSERT INTO category (name, description, sort, status) VALUES
  ('学业', '学业困惑、考试压力、选课经验', 1, 1),
  ('情感', '情感倾诉、人际关系', 2, 1),
  ('求职', '求职焦虑、实习经验', 3, 1),
  ('生活', '日常生活、提问交流', 4, 1);

INSERT INTO admin (username, password) VALUES
  ('admin', 'PLACEHOLDER_HASH');  -- 需替换为 bcrypt 加密后的密码
