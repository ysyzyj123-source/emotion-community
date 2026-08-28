# -*- coding: utf-8 -*-
"""发 5 个正向帖子用于测试情感趋势曲线。"""
import requests

BASE = "http://127.0.0.1:5000"

t = requests.post(f"{BASE}/api/auth/login",
                  json={"account": "零零零零零零", "password": "123456", "role": "student"}, timeout=10)
h = {"Authorization": f"Bearer {t.json()['data']['token']}"}

positive_posts = [
    "今天终于考完所有的试了，太开心了，轻松！",
    "顺利拿到offer，超级高兴幸福！",
    "和朋友一起去吃了好吃的，特别满足快乐！",
    "导师夸我进步很大，心里美滋滋的好开心！",
    "运动完心情特别好，满满正能量，加油！",
]

for i, content in enumerate(positive_posts, 1):
    r = requests.post(f"{BASE}/api/post", headers=h,
                      json={"title": f"正向测试{i}", "content": content}, timeout=10)
    print(f"第{i}帖: {r.status_code} {r.json()['data']['sentiment']} valence={r.json()['data'].get('valence')}")
