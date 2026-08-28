"""构建多任务训练语料（情感倾向 + 紧急程度 + 情感分值）。

数据融合：
  - 公开 ChnSentiCorp（上万条，情感倾向打底）：sentiment=0负/1正，emergency=0正常，valence 按情感映射
  - 校园多任务语料（补充紧急/关注样本 + 中文情感分值）：完整三标签

每条样本字段：text, sentiment(0负/1正/2中性), emergency(0正常/1关注/2紧急), valence(-10~+10)
输出：data/sentiment/multitask_{train,val}.jsonl
"""
import os
import json
import random

random.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment")
OUT_TRAIN = os.path.join(BASE, "multitask_train.jsonl")
OUT_VAL = os.path.join(BASE, "multitask_val.jsonl")
os.makedirs(BASE, exist_ok=True)

SENT_MAP = {"负向": 0, "正向": 1, "中性": 2}
EMG_MAP = {"正常": 0, "关注": 1, "紧急": 2}

# 校园多任务语料（完整三标签，含大量紧急/关注样本以解决类别不均衡）
CAMPUS = [
    ("期末考试挂科了，心情很低落", "负向", "正常", -6.0),
    ("复习压力大到喘不过气，好累", "负向", "正常", -5.0),
    ("和室友吵架了，心里很难受", "负向", "正常", -6.5),
    ("暗恋的人有对象了，好难过", "负向", "正常", -7.0),
    ("找工作投了好多简历没回音，很焦虑", "负向", "关注", -7.5),
    ("最近失眠焦虑，精神状态很差", "负向", "关注", -7.0),
    ("考研复习到崩溃，感觉坚持不下去了", "负向", "关注", -8.0),
    ("期末压力大，严重失眠，很痛苦", "负向", "关注", -8.5),
    ("我真的撑不下去了，想死，想结束这一切", "负向", "紧急", -10.0),
    ("活着太累了，我想轻生，想消失", "负向", "紧急", -10.0),
    ("好想跳楼，一了百了，解脱算了", "负向", "紧急", -10.0),
    ("最近被室友霸凌，真的想自杀", "负向", "紧急", -10.0),
    ("考研终于上岸了，太开心了！", "正向", "正常", 9.0),
    ("拿到奖学金了，特别激动，感谢自己", "正向", "正常", 8.5),
    ("和男朋友感情很好，很幸福", "正向", "正常", 7.0),
    ("找到实习了，前途光明，充满希望", "正向", "正常", 8.0),
    ("社团活动办得很成功，超有成就感", "正向", "正常", 7.5),
    ("和朋友出去玩很开心，心情舒畅", "正向", "正常", 7.0),
    ("今天去食堂吃了午饭，点了份菜", "中性", "正常", 0.0),
    ("下午上了两节课，记了笔记", "中性", "正常", 0.0),
    ("明天有数学课，提前预习了一下", "中性", "正常", 0.5),
    ("打开了电脑准备写作业", "中性", "正常", 0.0),
]

# 扩充紧急/关注样本（解决类别不均衡）
EMERGENCY_BOOST = [
    ("我快崩溃了，真的好想死", "负向", "紧急", -10.0),
    ("想轻生了，不想活了", "负向", "紧急", -10.0),
    ("一直在想自杀，控制不住", "负向", "紧急", -10.0),
    ("活不下去，想结束生命", "负向", "紧急", -10.0),
    ("绝望到想自我了结", "负向", "紧急", -10.0),
    ("伤害自己的念头越来越强", "负向", "紧急", -10.0),
    ("想从楼上跳下去", "负向", "紧急", -10.0),
    ("不想存在了，想消失", "负向", "紧急", -10.0),
    ("天天失眠焦虑到崩溃", "负向", "关注", -8.0),
    ("撑不住了，压力大到极点", "负向", "关注", -8.0),
    ("抑郁到什么都不想做", "负向", "关注", -7.5),
    ("极度痛苦，快扛不住了", "负向", "关注", -8.0),
    ("被孤立了，好绝望", "负向", "关注", -7.0),
    ("学业感情双重打击，快崩溃", "负向", "关注", -8.0),
]

# 反讽/强撑语料（表面积极实则消极，解决模型反讽盲区）
IRONY_BOOST = [
    ("挺好的，我没事，真的没事", "负向", "关注", -7.5),
    ("哈哈，生活对我真好呢", "负向", "关注", -7.5),
    ("没事，习惯一个人了", "负向", "关注", -6.5),
    ("fine，就这样吧", "负向", "正常", -5.5),
    ("无所谓，反正也没人在意", "负向", "关注", -6.8),
    ("都挺好的其实", "负向", "正常", -5.5),
    ("破防了家人们", "负向", "关注", -7.0),
    ("这房间好安静啊", "负向", "正常", -6.0),
    ("终于考完了，但好像也没多开心", "负向", "正常", -5.0),
    ("拿到offer了，却高兴不起来", "负向", "关注", -7.0),
    ("大家都夸我，可我一点感觉都没有", "负向", "关注", -6.5),
    ("哈哈，我好快乐啊（并不）", "负向", "关注", -7.0),
    ("太棒了，又挂了", "负向", "正常", -6.0),
    ("今天天气真好，适合消失", "负向", "紧急", -8.5),
    ("我爸说我不配，他说得对", "负向", "关注", -7.5),
    ("笑死，我根本不在乎", "负向", "正常", -5.0),
    ("开心，又是被骂的一天", "负向", "正常", -6.0),
    ("嗯嗯，我不难过，真的", "负向", "关注", -6.5),
    ("挺好，没朋友也挺自由", "负向", "关注", -6.5),
    ("我很好，我好得很", "负向", "关注", -6.0),
]


def load_public():
    """加载公开 ChnSentiCorp，情感打底，紧急=正常，分值按情感映射。"""
    rows = []
    try:
        from datasets import load_dataset
        ds = load_dataset("lansinuote/ChnSentiCorp")
        for split in ["train", "test"]:
            for item in ds[split]:
                label = int(item["label"])  # 0负面 1正面
                v = 7.0 if label == 1 else -6.0
                rows.append({
                    "text": item["text"],
                    "sentiment": label,
                    "emergency": 0,
                    "valence": v,
                })
    except Exception as e:
        print(f"公开数据加载失败: {e}，仅用校园语料")
    return rows


def build():
    rows = load_public()
    for text, sent, emg, val in CAMPUS:
        rows.append({
            "text": text,
            "sentiment": SENT_MAP[sent],
            "emergency": EMG_MAP[emg],
            "valence": val,
        })
    # 扩充紧急/关注样本
    for text, sent, emg, val in EMERGENCY_BOOST:
        rows.append({
            "text": text,
            "sentiment": SENT_MAP[sent],
            "emergency": EMG_MAP[emg],
            "valence": val,
        })
    # 扩充反讽/强撑样本
    for text, sent, emg, val in IRONY_BOOST:
        rows.append({
            "text": text,
            "sentiment": SENT_MAP[sent],
            "emergency": EMG_MAP[emg],
            "valence": val,
        })

    # 上采样紧急/关注样本（类别不均衡处理：复制多份提升比例）
    # emergency: 0正常(大量) 1关注(少) 2紧急(极少)
    UPSCALE = 40
    upsamped = []
    for r in rows:
        if r["emergency"] in (1, 2):  # 关注/紧急
            for _ in range(UPSCALE):
                upsamped.append(dict(r))
        else:
            upsamped.append(r)
    rows = upsamped

    random.shuffle(rows)
    val_size = max(1, int(len(rows) * 0.15))
    val, train = rows[:val_size], rows[val_size:]
    with open(OUT_TRAIN, "w", encoding="utf-8") as f:
        for r in train:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT_VAL, "w", encoding="utf-8") as f:
        for r in val:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"多任务语料: train={len(train)} val={len(val)} (含公开{f' {len(rows)}'*0}条混合)")


if __name__ == "__main__":
    build()
