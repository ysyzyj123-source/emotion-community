# -*- coding: utf-8 -*-
"""在现有40000条基础上，补充约2500条超短中性/无谓陈述语料。"""
import json, random
from collections import Counter

random.seed(7)
P = r'D:\毕设\代码\ml\data\sentiment\multitask_train.jsonl'
rows = [json.loads(l) for l in open(P, encoding='utf-8') if l.strip()]

# 超短中性 / 无谓陈述 / 应答
SHORT_NEUTRAL = [
    "我是一个人类", "我是学生", "我是老师", "我是个体",
    "这是我的想法", "就是这样", "事情已经发生了", "就这么定了",
    "嗯", "好的", "知道了", "哦", "原来如此", "明白了",
    "哈哈", "路过", "围观", "收到", "了解", "没事",
    "今天天气不错", "就这样吧", "没什么特别的", "随便说说",
    "我是普通人", "我来自北京", "我在上学", "这是个测试",
    "这是我的账号", "第一次发帖", "来看看", "打个卡",
    "今日打卡", "随便逛逛", "沉默", "无言", "走过路过",
    "测试测试", "水一下", "顶一下", "来了", "在吗",
    "有人吗", "大家好", "新人报道", "路过一下", "潜水",
    "我是谁", "从哪来", "到哪去", "天亮了", "月亮很圆",
    "风很大", "雨停了", "太阳升起来了", "地铁来了", "到站了",
    "上课了", "下课了", "放学了", "开会了", "散会了",
    "吃完了", "回家了", "到了", "出发了", "到了再说",
    "随缘吧", "顺其自然", "走一步看一步", "看情况", "再说吧",
    "差不多", "还行", "可以吧", "一般般", "没感觉",
    "不清楚", "不知道", "不确定", "无所谓", "随它去",
]

# 每条中性，紧急=正常，分值接近0
def add(rows, pool, sentiment=2, emergency=0, vmin=-0.8, vmax=0.8, scale=1):
    added = []
    for text in pool:
        for _ in range(max(1, scale)):
            rows.append({'text': text, 'sentiment': sentiment, 'emergency': emergency,
                         'valence': round(random.uniform(vmin, vmax), 1)})
            added.append(text)
    return added

# 每条模板生成多份以凑量（约2500条）
# pool含约50个基础句，每条生成50份 => 2500条
pool = SHORT_NEUTRAL
per = max(1, 2500 // len(pool))  # 2500/50 = 50
added = add(rows, pool, scale=per)
print(f"新增强短中性 {len(added)} 条 (基础句{len(pool)} × {per}份)")

random.shuffle(rows)
with open(P, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

sent = Counter(r['sentiment'] for r in rows)
emg = Counter(r['emergency'] for r in rows)
print(f"最终总条数: {len(rows)}")
print(f"  情感: 负={sent.get(0,0)} 正={sent.get(1,0)} 中性={sent.get(2,0)}")
print(f"  紧急: 正常={emg.get(0,0)} 关注={emg.get(1,0)} 紧急={emg.get(2,0)}")
