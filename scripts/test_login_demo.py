# -*- coding: utf-8 -*-
"""验证演示学生账号昵称登录。"""
import requests

def login(account, password):
    r = requests.post("http://127.0.0.1:5000/api/auth/login",
                      json={"account": account, "password": password, "role": "student"},
                      timeout=10)
    return r.status_code, r.json()

code, body = login("零零零零零零", "123456")
print("登录状态:", code, "| msg:", body.get("msg"))
if body.get("data"):
    print("role:", body["data"]["role"], "| user_id:", body["data"]["user_id"])
