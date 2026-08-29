"""多任务 BERT 情感推理服务（大模型式：情感/紧急/分值三输出）。

独立部署，监听 5051 端口。
接口: POST /predict  body: {"text": "..."}
返回: {
  "sentiment": 负向/正向/中性,
  "emergency": 正常/关注/紧急,
  "valence": -10~+10,
  "sentiment_probs": {...},   # 三分类概率
  "emergency_probs": {...},   # 三分类概率
}

用法（在 ml 目录）：
    .venv\\Scripts\\python.exe sentiment\\server.py
"""
import os
import sys

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, BertConfig

from model import MultiTaskBert

BASE = os.path.join(os.path.dirname(__file__), "..")
MODEL_DIR = os.path.join(BASE, "data", "models", "multitask_bert")

app = Flask(__name__)

SENT_LABELS = ["负向", "正向", "中性"]
EMG_LABELS = ["正常", "关注", "紧急"]

tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    global tokenizer, model
    config = BertConfig.from_pretrained(MODEL_DIR)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = MultiTaskBert.from_pretrained(MODEL_DIR, config=config)
    model.to(device)
    model.eval()
    print(f"多任务模型已加载，设备: {device}")


# 中文字符范围（用来判断文本是否"真的说了话"）
import re as _re
_CJK = _re.compile(r'[\u4e00-\u9fff]')
_LETTER = _re.compile(r'[A-Za-z]')

# 学术/专业中性陈述词（含这类词且无情绪词 -> 判断性陈述，归中性）
ACADEMIC_WORDS = [
    "研究", "系统", "基于", "算法", "设计", "实现", "模型", "分析",
    "架构", "开发", "流程", "模块", "数据库", "接口", "程序", "数据",
    "本项目", "论文", "章节", "文献", "实验", "测试", "方案", "功能",
]
# 情绪词（含情绪词则不是纯学术陈述，不归中性）
EMOTION_WORDS = [
    "难过", "开心", "高兴", "快乐", "幸福", "焦虑", "担心", "痛苦",
    "崩溃", "煎熬", "失眠", "烦躁", "郁闷", "生气", "绝望", "累",
    "爱", "喜欢", "恨", "想死", "自杀", "哭", "笑", "烦", "抗",
]

def is_repetitive_spam(text):
    """检测重复刷屏：去掉重复后句子过短（字符数 < 原始的30% 且原始长度>20）-> 视为刷屏。"""
    if len(text) < 20:
        return False
    # 去掉所有重复字符后的核心
    uniq = "".join(dict.fromkeys(text))  # 仅保留首次出现字符
    shorter = text[:80]
    # 统计出现>=3次的字符占比
    from collections import Counter
    cnt = Counter(shorter)
    repeats = sum(1 for ch, c in cnt.items() if c >= 3)
    # 若大量字符重复且有效中文少 -> 刷屏
    if repeats >= 3 and len(uniq) < max(5, len(shorter) // 3):
        return True
    # 单一短语重复（如"哈哈哈""今天太好了"...）
    # 取前6字，若全文本由该短语组成
    prefix6 = shorter[:6]
    if len(shorter) >= 18 and shorter.count(prefix6) >= 3:
        return True
    return False


def is_academic_neutral(text):
    """检测学术/专业中性陈述：含学术词 且 无情绪词 -> 判中性（避免学术描述被误判负向关注）。"""
    has_aca = any(w in text for w in ACADEMIC_WORDS)
    has_emo = any(w in text for w in EMOTION_WORDS)
    return has_aca and not has_emo


# 情绪词（含情绪词则不是纯客观陈述，保持模型判断，不归中性）
# 注意：只放真正的情绪词，不放"很/太/真的"等程度副词（否则几乎所有句子都含，规则失效）
EMOTION_WORDS = [
    # 负向情绪
    "难过", "伤心", "痛苦", "悲伤", "沮丧", "绝望", "烦躁", "郁闷", "焦虑",
    "担心", "害怕", "恐惧", "紧张", "崩溃", "煎熬", "委屈", "失落", "孤独",
    "寂寞", "空虚", "无助", "迷茫", "困惑", "纠结", "讨厌", "恨", "生气",
    "愤怒", "气死", "倒霉", "糟糕", "难受", "心痛", "失眠", "睡不着", "哭",
    "流泪", "叹气", "压力大", "想哭", "好烦", "好累", "emo", "抑郁", "烦死",
    # 正向情绪
    "开心", "高兴", "快乐", "幸福", "激动", "兴奋", "喜悦", "满足", "欣慰",
    "温暖", "感动", "喜欢", "爱", "舒服", "爽", "美好", "甜蜜", "幸福",
    "成功", "上岸", "幸运", "感恩", "感谢", "高兴坏了", "骄傲",
]

# 客观陈述/日程/事实类词（含这些且无情绪/网络梗/反问词才判中性）
# 涵盖：上课、日程、吃饭、交通、天气、物品、工作、场所等客观场景词
DESCRIPTIVE_WORDS = [
    # 日程/上课
    "上课", "下课", "自习", "听课", "讲座", "考试", "作业", "自习", "开会",
    "开会", "周报", "汇报", "项目", "论文", "课程", "实验", "图书馆",
    # 日常/吃饭
    "吃饭", "食堂", "外卖", "早餐", "午餐", "晚餐", "做饭", "点餐", "点外卖",
    # 交通/出行
    "地铁", "公交", "打车", "火车", "飞机", "到站", "出发", "坐车", "骑车", "走路",
    # 天气
    "下雨", "下雪", "晴天", "阴天", "刮风", "降温", "天气", "温度",
    # 物品/生活
    "快递", "取包裹", "买东西", "超市", "购物", "睡觉", "起床", "洗漱",
    "跑步", "散步", "健身", "锻炼", "打球", "唱歌", "玩", "休息",
    # 工作/事务
    "报", "写", "做", "买了", "更新", "版本", "功能", "配置",
    # 影视/推荐/分享
    "美剧", "电影", "剧", "视频", "看的", "推荐", "好看",
]

# 高危自伤词（含则绝不判中性，保证预警）
HIGH_RISK_ALL = [
    "自杀", "想死", "结束生命", "轻生", "割腕", "活不下去", "了结",
    "伤害自己", "跳楼", "消失", "不想活", "自残", "自我了结", "想不开", "死",
]

# 网络梗/情绪化表达词（含这些绝不判中性，避免误伤真实情绪）
SLANG_EMOTION = [
    "麻了", "栓Q", "起飞", "破防", "emo", "绷不住了", "yyds", "绝了",
    "笑死", "谁懂", "家人们", "泪目", "上头", "裂开", "摆烂", "躺平",
    "内卷", "卷死", "佛了", "我好", "我人", "我麻", "做错", "这样对我",
    "老天", "天呐", "天哪", "救命", "无语", "昏迷",
]
# 反问/感叹符号（含则说明有情绪色彩，不判中性）
RHETORIC_MARK = ["？", "?", "！", "!", "~", "～"]


def is_descriptive_neutral(text):
    """客观陈述/日程记录 -> 判中性。

    收紧条件：仅当满足以下全部才判中性，避免误伤真实情绪：
      - 文本长度 >= 8 字（太短交给模型）
      - 含客观陈述词（上课/吃饭/开会/下雨/坐车等日程/事实类）
      - 不含情绪词、网络梗、反问/感叹号（这些说明有情绪色彩）
      - 不含高危词
    """
    if len(text) < 8:
        return False
    if any(w in text for w in RHETORIC_MARK):
        return False
    if any(w in text for w in EMOTION_WORDS):
        return False
    if any(w in text for w in SLANG_EMOTION):
        return False
    if any(w in text for w in HIGH_RISK_ALL):
        return False
    # 含客观陈述词（日程/事实/描述类）才判中性
    has_desc = any(w in text for w in DESCRIPTIVE_WORDS)
    return has_desc


def clean_and_detect(text):
    """预处理：
    1. 纯符号/无意义文本（有效字母<3）-> 判中性
    2. 重复刷屏（连续重复短语）-> 判中性
    3. 学术/专业中性陈述（含学术词且无情绪词）-> 判中性
    4. 客观陈述/推荐（无情绪词且无高危词）-> 判中性
    返回 (清理后文本, 是否判定中性)。
    """
    text = _re.sub(r'\s+', ' ', text).strip()
    zh = len(_CJK.findall(text))
    en = len(_LETTER.findall(text))
    total_letters = zh + en
    if total_letters < 3:
        return text, True
    if is_repetitive_spam(text):
        return text, True
    if is_academic_neutral(text):
        return text, True
    # 客观陈述/推荐/分享（无情绪词且无高危词）-> 中性
    if is_descriptive_neutral(text):
        return text, True
    return text, False


def trunk_long_text(text, max_chars=180):
    """超长文本改进截断：取开头和结尾各约一半，避免只留前段丢失语义。
    BERT max_length=128 token，中文约128字；这里先按字符数粗截，
    长文本取首尾各半，保证语义完整。
    """
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + text[-half:]


@app.post("/predict")
def predict():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is empty"}), 400

    # ---- 预处理：纯符号/无意义文本 -> 直接判中性（避免误报预警）----
    cleaned, is_noisy = clean_and_detect(text)
    if is_noisy:
        return jsonify({
            "sentiment": "中性", "emergency": "正常", "valence": 0.0,
            "sentiment_probs": {"负向": 0.0, "正向": 0.0, "中性": 1.0},
            "emergency_probs": {"正常": 1.0, "关注": 0.0, "紧急": 0.0},
        })

    # ---- 超长文本改进截断：首尾各半采样（避免只取前段丢失语义）----
    text = trunk_long_text(text)
    inputs = tokenizer(text, truncation=True, padding=True, max_length=128, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs)

    sent_logits = out["sentiment_logits"][0]
    emg_logits = out["emergency_logits"][0]
    valence = out["valence"][0].item()

    sent_probs = torch.softmax(sent_logits, dim=-1)
    emg_probs = torch.softmax(emg_logits, dim=-1)

    sent_idx = int(torch.argmax(sent_probs))
    emg_idx = int(torch.argmax(emg_probs))

    # 置信度兜底：模型对情感判断"没把握"（最高概率低于阈值）时，
    # 归为中性/正常/分值0，避免生僻/无上下文内容被乱判成负向或预警。
    sent_conf = float(max(float(x) for x in sent_probs))
    emg_conf = float(max(float(x) for x in emg_probs))
    if sent_conf < SENT_CONF_THRESHOLD:
        sent_idx = 2  # 中性
    if emg_conf < EMG_CONF_THRESHOLD:
        emg_idx = 0  # 正常

    # 规则兜底：命中高危自伤关键词则强制判紧急（保证高危不遗漏）
    if HIGH_RISK_WORDS and any(w in text for w in HIGH_RISK_WORDS):
        emg_idx = 2  # 紧急

    # 分级校准：把模型原始 valence 映射到严谨的三级区间
    valence = calibrate_valence(text, SENT_LABELS[sent_idx], EMG_LABELS[emg_idx], valence)

    return jsonify({
        "sentiment": SENT_LABELS[sent_idx],
        "emergency": EMG_LABELS[emg_idx],
        "valence": round(float(valence), 2),
        "sentiment_probs": {SENT_LABELS[i]: round(float(sent_probs[i]), 4) for i in range(3)},
        "emergency_probs": {EMG_LABELS[i]: round(float(emg_probs[i]), 4) for i in range(3)},
    })


# ===== 分级校准：三层情绪强度 =====
# 三级区间（负面）：轻度抱怨(0~-5)  中度负面(-5~-8)  重度高危(-8~-10)
# 正向：0~+5 轻度正面 / +5~+10 强烈正面
INTENSIFIERS = ["很", "特别", "非常", "极度", "超级", "崩溃", "绝望",
                "痛苦", "受不了", "撑不住", "扛不住", "要死", "极", "巨", "完全"]


def calibrate_valence(text, sentiment, emergency, raw_valence):
    """以模型原始分值为基础，做区间校准（不重写，只修正越界/不合理）。

    原则：尊重模型语义判断，仅把分值约束到与情感倾向/紧急度相符的区间，
    避免"轻度抱怨被打到 -7"或"高危只给 -3"这类不合理。
    """
    # 高危紧急：强制重度区间 [-10,-8.5]
    if emergency == "紧急":
        return min(raw_valence, -8.5) if raw_valence < -8 else -9.2

    # 正向
    if sentiment == "正向":
        # 反讽检测：表面积极但含消极词/转折 -> 负向
        if any(w in text for w in ["没事", "挺好", "习惯", "无所谓", "fine", "哈哈", "不在乎", "笑死", "并"]) \
           and any(w in text for w in ["难过", "消失", "死", "骂", "落", "空", "孤单", "累", "差"]):
            return -4.0
        # 正常正向：约束在 [1, +9.5]，强度词上抬
        v = max(1.0, raw_valence)
        if any(w in text for w in INTENSIFIERS):
            v = max(v, 6.0)
        return min(9.5, v)

    # 负向
    if sentiment == "负向":
        v = min(0.0, raw_valence)  # 负向分值不得为正
        # 轻度抱怨（无高强度词、紧急度为正常）约束到 [-5, 0]
        if emergency == "正常" and not any(w in text for w in INTENSIFIERS):
            return max(-5.0, v)
        # 中度偏重：约束到 [-8, 0]
        return max(-8.0, v)

    # 中性：贴近 0
    return round(raw_valence * 0.4, 2)


# 高危自伤关键词（规则兜底，命中即紧急）
HIGH_RISK_WORDS = [
    "自杀", "想死", "结束生命", "轻生", "割腕", "活不下去", "了结",
    "伤害自己", "跳楼", "消失", "不想活", "自残", "自我了结", "想不开",
]

# 置信度兜底阈值：情感/紧急的分类最高概率低于该值时，视为"没把握"，归中性/正常
SENT_CONF_THRESHOLD = 0.60   # 情感三分类最高概率 < 0.60 -> 中性
EMG_CONF_THRESHOLD = 0.55    # 紧急三分类最高概率 < 0.55 -> 正常


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5051, debug=False)
