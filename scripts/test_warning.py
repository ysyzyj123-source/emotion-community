# -*- coding: utf-8 -*-
"""测试预警工作台：老师查看/处理预警，学生无权访问。"""
import requests

BASE = "http://127.0.0.1:5000"

def login(account, password, role):
    r = requests.post(f"{BASE}/api/auth/login", json={"account": account, "password": password, "role": role}, timeout=10)
    return r.json()["data"]["token"]

# 老师
teacher_t = login("T1001", "123456", "teacher")
th = {"Authorization": f"Bearer {teacher_t}"}

# 学生
student_t = login("零零零零零零", "123456", "student")
sh = {"Authorization": f"Bearer {student_t}"}

# 1. 老师查看预警列表
r = requests.get(f"{BASE}/api/warning/list", headers=th, timeout=10)
print("== 预警列表 ==", r.status_code, "共", len(r.json()["data"]["items"]), "条")
for it in r.json()["data"]["items"]:
    print("  ", it["warning_id"], "| post", it["post_id"], "|", it["emergency"], "| status", it["status"], "|", it["title"])

# 2. 统计
r = requests.get(f"{BASE}/api/warning/stats", headers=th, timeout=10)
print("== 统计 ==", r.json()["data"])

# 3. 学生访问被拒
r = requests.get(f"{BASE}/api/warning/list", headers=sh, timeout=10)
print("== 学生访问(应403) ==", r.status_code, r.json()["msg"])

# 4. 预警详情
items = requests.get(f"{BASE}/api/warning/list", headers=th, timeout=10).json()["data"]["items"]
if items:
    wid = items[0]["warning_id"]
    r = requests.get(f"{BASE}/api/warning/{wid}", headers=th, timeout=10)
    d = r.json()["data"]
    print("== 预警%d详情 ==" % wid, "status", d["status"], "| 帖:", d["post"]["title"], "| 情感", d["post"]["sentiment"])

    # 5. 跟进处理
    r = requests.post(f"{BASE}/api/warning/{wid}/handle", headers=th, json={"note": "已联系辅导员跟进，安排心理谈话", "status": 1}, timeout=10)
    print("== 处理预警 ==", r.status_code, r.json())

    # 6. 处理后再看详情
    r = requests.get(f"{BASE}/api/warning/{wid}", headers=th, timeout=10)
    print("== 处理后 ==", "status", r.json()["data"]["status"], "| 处理记录", r.json()["data"]["handle_note"])
