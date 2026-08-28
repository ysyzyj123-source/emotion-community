"""生成校园情感训练语料（组合扩充版）。

用"场景词 × 情绪表达"组合批量生成，扩充到千条量级，
覆盖四大场景、三种情感，并含高危紧急样本。
用于二次微调 BERT，让模型更懂校园表达。
"""
import os
import json
import random

random.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment")
OUT = os.path.join(BASE, "campus_train.jsonl")
OUT_VAL = os.path.join(BASE, "campus_val.jsonl")
os.makedirs(BASE, exist_ok=True)

# ===== 场景主题词 =====
SUBJECTS = ["考试", "复习", "绩点", "论文", "选课", "考研", "作业", "小组作业",
            "室友", "宿舍", "恋爱", "暗恋", "分手", "表白", "社团", "兼职",
            "实习", "面试", "简历", "offer", "奖学金", "老师", "同学", "家人"]

# ===== 正向情绪表达（带 sujeto） =====
POS_PATTERNS = [
    "{s}很顺利，特别开心！",
    "{s}做得很好，超有成就感！",
    "{s}有了好消息，幸福得不得了！",
    "{s}很满意，心里美滋滋的！",
    "{s}终于搞定了，一身轻松，太高兴了！",
    "{s}进展不错，充满斗志，加油！",
    "{s}很温暖，觉得被关怀，很快乐。",
    "{s}让我很有信心，特别棒！",
    "{s}成功了，感谢一直没有放弃的自己！",
    "{s}超出预期，惊喜又满足！",
]

# ===== 负向普通情绪表达 =====
NEG_PATTERNS = [
    "{s}压力太大，有点喘不过气，好累。",
    "{s}不顺心，心情很低落，有点沮丧。",
    "{s}出了问题，心里很烦躁，难受。",
    "{s}让我很焦虑，晚上都睡不好。",
    "{s}很难过，觉得自己不行，很自卑。",
    "{s}很烦，看什么都不顺眼，提不起劲。",
    "{s}很压抑，想找个地方躲起来。",
    "{s}让我很委屈，心里堵得慌。",
    "{s}很痛苦，感觉快撑不住了。",
    "{s}让人绝望，看不到希望，好失望。",
]

# ===== 中性表达 =====
NEU_PATTERNS = [
    "今天处理了{s}相关的事情，按部就班。",
    "下午安排了关于{s}的任务，正常进行。",
    "{s}的事情普普通通，没什么特别。",
    "我对{s}没什么感觉，照常过。",
    "今天记录了{s}的一些安排，很平常。",
]

# ===== 高危紧急语料(独立) =====
HIGH_RISK = [
    "我真的撑不下去了，想死，结束这一切吧。",
    "活着太累了，我想轻生，想消失。",
    "好想跳楼，一了百了，解脱算了。",
    "我已经割腕了，感觉不到痛，只想结束生命。",
    "我不想活了，想自杀，请大家远离我。",
    "活不下去，我想伤害自己，结束痛苦。",
    "感觉自己没救了，想自我了结。",
    "每天都很绝望，想死的心越来越强烈。",
    "我想从楼上跳下去，结束这痛苦的一切。",
    "撑不住了，想结束自己的生命，对不起所有人。",
    "最近被室友霸凌，真的好想死。",
    "考试全挂，活不下去了，想自杀。",
    "分手后好痛苦，想结束生命。",
    "找不到工作，绝望到想轻生。",
    "和家里断绝往来了，想自我了结。",
]


def build():
    rows = []
    for s in SUBJECTS:
        for p in POS_PATTERNS:
            rows.append({"text": p.format(s=s), "label": 1, "emergency": "正常"})
        for p in NEG_PATTERNS:
            rows.append({"text": p.format(s=s), "label": 0, "emergency": "正常"})
        for p in NEU_PATTERNS:
            rows.append({"text": p.format(s=s), "label": 1, "emergency": "正常"})
    for t in HIGH_RISK:
        rows.append({"text": t, "label": 0, "emergency": "紧急"})
    return rows


def main():
    rows = build()
    random.shuffle(rows)
    val_size = int(len(rows) * 0.15)
    val, train = rows[:val_size], rows[val_size:]
    with open(OUT, "w", encoding="utf-8") as f:
        for r in train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT_VAL, "w", encoding="utf-8") as f:
        for r in val:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    neg = sum(1 for r in train if r["label"] == 0)
    pos = sum(1 for r in train if r["label"] == 1)
    emg = sum(1 for r in train if r["emergency"] == "紧急")
    print(f"校园语料生成: train={len(train)} val={len(val)} (正{pos} 负{neg} 紧急{emg})")


if __name__ == "__main__":
    main()
