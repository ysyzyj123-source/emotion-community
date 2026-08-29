"""融合多任务训练语料：真实心理倾诉(cpsdd) + 校园人工语料。

数据组成：
  - cpsdd_train.jsonl (70005条)：真实中文心理倾诉，负向/关注/紧急，带真实严重度分值
  - 人工 POSITIVE/MILD/IRONY/HIGH_RISK：正向、轻度抱怨、反讽、高危（补充 cpsdd 缺失的区间）

输出：data/sentiment/multitask_{train,val}.jsonl
"""
import os
import json
import random

random.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment")
OUT_TRAIN = os.path.join(BASE, "multitask_train.jsonl")
OUT_VAL = os.path.join(BASE, "multitask_val.jsonl")
CPSDD_FILE = os.path.join(BASE, "cpsdd_train.jsonl")

SENT_MAP = {"负向": 0, "正向": 1, "中性": 2}
EMG_MAP = {"正常": 0, "关注": 1, "紧急": 2}

# 人工语料（补充 cpsdd 缺失的正向/轻度/反讽）
POSITIVE_BOOST = [
    ("考研上岸了，成功被录取，太棒了！", "正向", "正常", 9.0),
    ("拿到国家奖学金，特别感谢自己的努力", "正向", "正常", 8.5),
    ("终于拿到心仪的 offer 了，太开心了！", "正向", "正常", 8.5),
    ("表白成功，她答应做我女朋友，好幸福", "正向", "正常", 9.0),
    ("比赛获奖了，团队一起努力的结果", "正向", "正常", 8.0),
    ("论文被接收了，学术生涯新起点", "正向", "正常", 8.5),
    ("绩点拿了第一，太有成就感了", "正向", "正常", 8.0),
    ("和喜欢的人在一起了，每天都好甜", "正向", "正常", 9.0),
    ("拿到了保研资格，激动得睡不着", "正向", "正常", 9.0),
    ("通过了英语六级，太高兴了", "正向", "正常", 7.5),
]
MILD_BOOST = [
    ("今天作业好多，写不完了", "负向", "正常", -4.0),
    ("早上还要上早八，好累", "负向", "正常", -3.0),
    ("食堂的饭又涨价了，讨厌", "负向", "正常", -2.0),
    ("wifi 又断了，网课卡死", "负向", "正常", -1.5),
    ("这个老师讲得好无聊", "负向", "正常", -1.0),
    ("又要小组作业，又要组队好烦", "负向", "正常", -3.5),
    ("宿舍太吵了，睡不好", "负向", "正常", -3.0),
    ("电脑卡死了，好烦", "负向", "正常", -2.0),
    ("今天状态好差，不在状态", "负向", "正常", -3.5),
    ("外卖送超时了，饿死了", "负向", "正常", -2.5),
]
IRONY_BOOST = [
    ("挺好的，我没事，真的没事", "负向", "关注", -7.5),
    ("哈哈，生活对我真好呢", "负向", "关注", -7.5),
    ("没事，习惯一个人了", "负向", "关注", -6.5),
    ("fine，就这样吧", "负向", "正常", -5.5),
    ("无所谓，反正也没人在意", "负向", "关注", -6.8),
    ("破防了家人们", "负向", "关注", -7.0),
    ("拿到offer了，却高兴不起来", "负向", "关注", -7.0),
    ("大家都夸我，可我一点感觉都没有", "负向", "关注", -6.5),
    ("笑死，我根本不在乎", "负向", "正常", -5.0),
    ("我很好，我好得很", "负向", "关注", -6.0),
]

# —— 批量生成正向语料（约2000条，对抗负向） ——
POS_ACHIEVEMENTS = ["考研上岸", "拿到奖学金", "拿到offer", "表白成功", "比赛获奖", "论文通过",
                    "绩点第一", "保研成功", "英语六级通过", "offer确定", "考试全过", "实习转正",
                    "梦想成真", "获得证书", "社团评优", "运动会获奖", "拿到驾照", "学会新技能",
                    "社团活动圆满", "答辩顺利通过", "成功入党", "选上课程", "拿到专利"]
POS_EXP = ["太开心了", "特别幸福", "超有成就感", "激动得睡不着", "太棒了", "特别满意",
           "高兴坏了", "充满希望", "很自豪", "非常激动", "喜极而泣", "心花怒放",
           "乐开了花", "意气风发", "干劲十足"]


def gen_positive():
    rows = []
    for a in POS_ACHIEVEMENTS:
        for e in POS_EXP:
            rows.append({"text": f"{a}，{e}！", "sentiment": 1, "emergency": 0, "valence": round(random.uniform(6.5, 9.5), 1)})
    return sample_to(rows, 2000)


# —— 批量生成中性语料（约2000条） ——
NEU_SCENES = ["今天去食堂吃了午饭", "下午上了两节课", "明天有数学课", "去图书馆借了书",
              "买了杯奶茶", "在操场走了一圈", "写完了作业", "收拾了宿舍", "开了个会", "看了会书",
              "整理了笔记", "去了趟超市", "洗了个澡", "刷了会手机", "做了顿饭", "交了作业",
              "听了讲座", "去实验室", "复印了资料", "订了外卖", "回宿舍休息", "去上课"]
NEU_EXP = ["没什么特别的", "挺平常的", "按部就班", "普普通通", "就这样", "照常进行",
           "很平静", "没什么感觉", "日常如此", "一切如常"]


def gen_neutral():
    rows = []
    for s in NEU_SCENES:
        for e in NEU_EXP:
            rows.append({"text": f"{s}，{e}。", "sentiment": 2, "emergency": 0, "valence": round(random.uniform(-1.5, 1.5), 1)})
    return sample_to(rows, 2000)


# —— 批量生成轻度抱怨语料（约2000条，分值 -1~-5） ——
MILD_TOPICS = ["作业好多", "上早八好累", "食堂涨价", "网卡死了", "课很无聊", "小组作业烦", "宿舍太吵",
               "电脑卡死", "状态好差", "外卖超时", "排队好久", "忘带钥匙", "空调坏了", "下雨没伞",
               "车没电", "考试难", "课表太满", "水卡丢了", "耳机坏了", "被子没晒"]
MILD_EXP = ["好烦", "真讨厌", "有点烦", "好无奈", "真是的", "烦死了", "好郁闷", "真不顺",
            "有点烦人", "好气人"]


def gen_mild():
    rows = []
    for t in MILD_TOPICS:
        for e in MILD_EXP:
            rows.append({"text": f"{t}，{e}。", "sentiment": 0, "emergency": 0, "valence": round(random.uniform(-4.5, -1.0), 1)})
    return sample_to(rows, 2000)


# —— 批量生成反讽/强撑语料（约2000条） ——
IRONY_TEMPLATES = [
    ("挺好的，我没事，真的没事", -7.5, 1), ("哈哈，生活对我真好呢", -7.5, 1), ("没事，习惯一个人了", -6.5, 1),
    ("fine，就这样吧", -5.5, 0), ("无所谓，反正也没人在意", -6.8, 1), ("破防了家人们", -7.0, 1),
    ("拿到offer了，却高兴不起来", -7.0, 1), ("大家都夸我，可我一点感觉都没有", -6.5, 1),
    ("笑死，我根本不在乎", -5.0, 0), ("我很好，我好得很", -6.0, 1),
]
IRONY_SUBJ = ["考试", "考研", "答辩", "实习", "面试", "比赛", "作业", "人际", "感情", "社团"]


def gen_irony():
    rows = []
    for base, val, emg in IRONY_TEMPLATES:
        for s in IRONY_SUBJ:
            rows.append({"text": f"{base}（{s}）", "sentiment": 0, "emergency": emg, "valence": val + random.uniform(-0.5, 0.5)})
    return sample_to(rows, 2000)


def sample_to(rows, target):
    """把列表采样/补齐到目标数量。"""
    if len(rows) >= target:
        return random.sample(rows, target)
    while len(rows) < target:
        rows.append(dict(random.choice(rows)))
    return rows


def load_cpsdd():
    """加载 cpsdd 真实倾诉语料（采样 5000 条，避免负向主导）。"""
    rows = []
    with open(CPSDD_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    # 随机采样 5000 条，保留严重度梯度
    if len(rows) > 5000:
        rows = random.sample(rows, 5000)
    return rows


def add_human(rows):
    # 保留原始手工标注的高危/反讽核心样本
    for t, sent, emg, val in POSITIVE_BOOST + MILD_BOOST + IRONY_BOOST:
        rows.append({
            "text": t,
            "sentiment": SENT_MAP[sent],
            "emergency": EMG_MAP[emg],
            "valence": val,
        })
    # 每种人工语料各约 2000 条（正向/中性/轻度/反讽）
    rows.extend(gen_positive())   # 2000 正向
    rows.extend(gen_neutral())    # 2000 中性
    rows.extend(gen_mild())       # 2000 轻度抱怨
    rows.extend(gen_irony())      # 2000 反讽/强撑
    return rows


def main():
    rows = load_cpsdd()
    add_human(rows)
    random.shuffle(rows)
    val_size = max(1, int(len(rows) * 0.1))
    val, train = rows[:val_size], rows[val_size:]
    with open(OUT_TRAIN, "w", encoding="utf-8") as f:
        for r in train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT_VAL, "w", encoding="utf-8") as f:
        for r in val:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"融合语料: train={len(train)} val={len(val)}")


if __name__ == "__main__":
    main()
