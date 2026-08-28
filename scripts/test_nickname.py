# -*- coding: utf-8 -*-
"""测试昵称宽度校验（用 Python requests 发送，避免终端编码干扰）。"""
import requests

BASE = "http://127.0.0.1:5000/api/auth/register"

cases = [
    ("6个汉字(应201)", "零零零零零零"),
    ("7个汉字(应400)", "零零零零零零零"),
    ("12字母(应201)", "abcdefghijkl"),
    ("13字母(应400)", "abcdefghijklm"),
    ("混合6宽(应400)", "零零零abcd1234"),
]

for label, nickname in cases:
    try:
        r = requests.post(BASE, json={"nickname": nickname, "password": "123456"}, timeout=10)
        print(f"{label:16s} -> HTTP {r.status_code}  {r.json().get('msg')}")
    except Exception as e:
        print(f"{label:16s} -> 异常 {e}")
