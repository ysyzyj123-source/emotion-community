# -*- coding: utf-8 -*-
"""测试数据看板接口。"""
import requests

BASE = "http://127.0.0.1:5000"

def login(account, password, role):
    r = requests.post(f"{BASE}/api/auth/login", json={"account": account, "password": password, "role": role}, timeout=10)
    return r.json()["data"]["token"]

th = {"Authorization": f"Bearer {login('T1001','123456','teacher')}"}
sh = {"Authorization": f"Bearer {login('零零零零零零','123456','student')}"}
ah = {"Authorization": f"Bearer {login('admin','admin123','admin')}"}

# 1. 情感趋势
r = requests.get(f"{BASE}/api/dashboard/sentiment-trend?days=7", headers=th, timeout=10)
print("== 情感趋势 ==", r.status_code)
d = r.json()["data"]
print("  日期:", d["labels"])
print("  正向:", d["正向"])
print("  负向:", d["负向"])

# 2. 话题分布
r = requests.get(f"{BASE}/api/dashboard/topic-distribution", headers=th, timeout=10)
print("== 话题分布 ==", r.status_code, r.json()["data"])

# 3. 概览
r = requests.get(f"{BASE}/api/dashboard/post-stats", headers=th, timeout=10)
print("== 概览 ==", r.status_code, r.json()["data"])

# 4. 学生访问被拒
r = requests.get(f"{BASE}/api/dashboard/sentiment-trend", headers=sh, timeout=10)
print("== 学生访问(应403) ==", r.status_code, r.json()["msg"])

# 5. 管理员可访问
r = requests.get(f"{BASE}/api/dashboard/topic-distribution", headers=ah, timeout=10)
print("== 管理员访问 ==", r.status_code, "OK")
