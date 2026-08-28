# -*- coding: utf-8 -*-
"""测试发帖功能：登录 -> 发帖(情感分析/话题分流) -> 列表 -> 详情。"""
import requests

BASE = "http://127.0.0.1:5000"

# 登录学生
r = requests.post(f"{BASE}/api/auth/login", json={"account": "零零零零零零", "password": "123456", "role": "student"}, timeout=10)
token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}
print("== 登录学生 ==", r.status_code, r.json()["msg"])

# 发帖1：负向紧急（含自杀词）
r = requests.post(f"{BASE}/api/post", headers=headers, json={
    "title": "最近真的好难",
    "content": "考试挂科了，感觉坚持不下去，有时候甚至想死，好无助",
}, timeout=10)
print("== 发帖1(负向紧急) ==", r.status_code, r.json())

# 发帖2：学业正向
r = requests.post(f"{BASE}/api/post", headers=headers, json={
    "title": "考研上岸啦",
    "content": "考研终于通过了，特别开心，感谢一直坚持的自己",
}, timeout=10)
print("== 发帖2(学业正向) ==", r.status_code, r.json())

# 发帖3：求职
r = requests.post(f"{BASE}/api/post", headers=headers, json={
    "title": "面试经验分享",
    "content": "今天去面试了一家公司，简历和面试流程都挺顺利的，分享下求职经验",
}, timeout=10)
print("== 发帖3(求职) ==", r.status_code, r.json())

# 列表
r = requests.get(f"{BASE}/api/post/list", headers=headers, timeout=10)
print("== 帖子列表 ==", r.status_code, "总数:", r.json()["data"]["total"])

# 详情（第一个帖子）
items = r.json()["data"]["items"]
if items:
    pid = items[0]["post_id"]
    r = requests.get(f"{BASE}/api/post/{pid}", headers=headers, timeout=10)
    print("== 帖子详情 id=%s ==" % pid, r.status_code, r.json()["data"])

# 板块列表
r = requests.get(f"{BASE}/api/post/categories", headers=headers, timeout=10)
print("== 板块列表 ==", r.status_code, r.json()["data"])
