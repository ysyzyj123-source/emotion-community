# -*- coding: utf-8 -*-
"""测试回复 + 积分激励。"""
import requests

BASE = "http://127.0.0.1:5000"

def login(account, password, role="student"):
    r = requests.post(f"{BASE}/api/auth/login", json={"account": account, "password": password, "role": role}, timeout=10)
    return r.json()["data"]["token"], r.json()["data"]

# 两个学生
t1, u1 = login("零零零零零零", "123456")
h1 = {"Authorization": f"Bearer {t1}"}

# 注册第二个学生
r = requests.post(f"{BASE}/api/auth/register", json={"nickname": "小暖", "password": "123456"}, timeout=10)
print("注册小暖:", r.status_code, r.json()["msg"])

t2, u2 = login("小暖", "123456")
h2 = {"Authorization": f"Bearer {t2}"}
print("小暖登录:", u2.get("user_id"))

# 学生1 再发一帖（方便学生2回复）
r = requests.post(f"{BASE}/api/post", headers=h1, json={
    "title": "求安慰", "content": "最近期末压力好大，好焦虑，感觉撑不住了",
}, timeout=10)
pid = r.json()["data"]["post_id"]
print("学生1发帖 id:", pid, r.json()["data"])

# 查看学生1发帖后的积分
r = requests.get(f"{BASE}/api/user/profile", headers=h1, timeout=10)
print("发帖后 学生1 profile:", r.json()["data"])

# 学生2 回复
r = requests.post(f"{BASE}/api/reply/{pid}", headers=h2, json={"content": "别难过，一起加油，会过去的"}, timeout=10)
print("学生2回复:", r.status_code, r.json())

# 再查看双方积分
r = requests.get(f"{BASE}/api/user/profile", headers=h2, timeout=10)
print("回复后 学生2 profile:", r.json()["data"])  # 应 +2
r = requests.get(f"{BASE}/api/user/profile", headers=h1, timeout=10)
print("回复后 学生1 profile:", r.json()["data"])  # 应 +3 (post_replied)

# 查看帖子回复列表
r = requests.get(f"{BASE}/api/reply/post/{pid}", headers=h1, timeout=10)
print("帖子回复列表:", r.json()["data"]["items"])

# 学生2 查看积分明细
r = requests.get(f"{BASE}/api/user/points/records", headers=h2, timeout=10)
print("学生2积分明细:", r.json()["data"]["items"])
