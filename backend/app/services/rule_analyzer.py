"""关键词规则降级分析器。

当 BERT / LDA 独立模型服务未部署或请求失败时，用轻量关键词规则给出
情感倾向、紧急程度与话题标签，保证功能链路可用。模型服务接入后，
此逻辑自动失效（见 ml_service.py 的优先级）。

规则仅供参考演示，真实项目以微调 BERT + LDA 为准。
"""

# 负面情绪关键词（按强度分级）
NEGATIVE_WORDS = [
    "难过", "崩溃", "绝望", "难受", "痛苦", "焦虑", "抑郁", "压抑",
    "想哭", "孤独", "害怕", "无助", "失眠", "窒息", "累死", "内耗",
    "想不开", "撑不住", "坚持不下去", "没意思", "很累",
]
NEGATIVE_EMERGENCY_WORDS = [
    "自杀", "想死", "结束生命", "轻生", "割腕", "活不下去", "了结",
    "伤害自己", "跳楼", "消失", "不想活",
]

# 正向关键词
POSITIVE_WORDS = [
    "开心", "高兴", "快乐", "成功", "通过", "顺利", "加油", "感谢",
    "幸福", "满意", "棒", "幸运", "谢谢", "喜欢",
]

# 话题关键词映射（词 -> 板块名）
TOPIC_KEYWORDS = {
    "学业": ["考试", "绩点", "挂科", "复习", "作业", "论文", "选课", "考研", "学习", "专业", "课程"],
    "情感": ["分手", "恋爱", "喜欢", "暧昧", "吵架", "孤独", "暗恋", "前任", "心动", "关系"],
    "求职": ["实习", "面试", "简历", "offer", "找工作", "笔试", "offer", "求职", "工资", "offer"],
    "生活": ["吃饭", "宿舍", "食堂", "作息", "运动", "减肥", "周末", "日常", "吐槽", "生活"],
}


def _count_words(text, words):
    return sum(1 for w in words if w in text)


def analyze_sentiment(text: str) -> dict:
    """返回 {sentiment, emergency, score, valence}。

    分值 valence 取值 -10~+10：
      - 负向：负数，越负面越接近 -10
      - 正向：正数，越正面越接近 +10
      - 中性：接近 0
    """
    neg = _count_words(text, NEGATIVE_WORDS)
    pos = _count_words(text, POSITIVE_WORDS)
    emergency_hits = _count_words(text, NEGATIVE_EMERGENCY_WORDS)

    if emergency_hits > 0:
        return {"sentiment": "负向", "emergency": "紧急", "score": 1.0, "valence": -10.0}
    if neg > 0:
        emergency = "关注" if neg >= 2 else "正常"
        score = min(0.9, 0.3 + neg * 0.2)
        valence = max(-9.0, -(2.0 + neg * 2.0))
        return {"sentiment": "负向", "emergency": emergency, "score": round(score, 2), "valence": round(valence, 1)}
    if pos > 0:
        valence = min(9.0, 2.0 + pos * 2.0)
        return {"sentiment": "正向", "emergency": "正常", "score": 0.0, "valence": round(valence, 1)}
    return {"sentiment": "中性", "emergency": "正常", "score": 0.0, "valence": 0.0}


def analyze_topic(text: str) -> dict:
    """返回 {topic_label, category}，按关键词命中数最多的板块判定。"""
    best_category, best_hits = None, 0
    for category, words in TOPIC_KEYWORDS.items():
        hits = _count_words(text, words)
        if hits > best_hits:
            best_category, best_hits = category, hits
    if best_category is None:
        return {"topic_label": "生活", "category": "生活"}
    return {"topic_label": best_category, "category": best_category}
