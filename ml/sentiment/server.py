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


@app.post("/predict")
def predict():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is empty"}), 400

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
