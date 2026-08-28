# -*- coding: utf-8 -*-
"""测试情感分值 valence (-10~+10) 与情感趋势接口。"""
import requests

BASE = "http://127.0.0.1:5000"

def login(a, p, role):
    r = requests.post(f"{BASE}/api/auth/login", json={"account": a, "password": p, "role": role}, timeout=10)
    return r.json()["data"]["token"]

sh = {"Authorization": f"Bearer {login('零零零零零零','123456','student')}"}
th = {"Authorization": f"Bearer {login('T1001','123456','teacher')}"}

# 发三条不同情感的帖子，检查返回 valence
tests = [
    ("正面测试", "今天考研通过了特别开心满意幸福"),
    ("负面测试", "我好难过很焦虑失眠内耗撑不住"),
    ("中性测试", "今天去食堂吃了顿饭"),
]
for title, content in tests:
    r = requests.post(f"{BASE}/api/post", headers=sh, json={"title": title, "content": content}, timeout=10)
    d = r.json()["data"]
    print(f"发帖[{title}] -> sentiment={d['sentiment']}")

# 查看数据库 valence
import subprocess
print("\n=== 数据库 sentiment_result valence 值 ===")

# 情感趋势
r = requests.get(f"{BASE}/api/dashboard/sentiment-trend?days=7", headers=th, timeout=10)
d = r.json()["data"]
print("== 情感趋势 ==")
print("labels:", d["labels"])
print("values:", d["values"])
print("range: min={} max={}".format(d["min"], d["max"]))
