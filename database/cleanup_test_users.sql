-- 清理注册/登录测试产生的残留账号
-- 保留 id=7（干净的中文昵称演示账号），删除历史乱码测试账号
USE emotion_community;

DELETE FROM user WHERE id IN (1, 2, 3, 4, 5, 6);

-- 查看剩余用户
SELECT id, nickname FROM user ORDER BY id;
