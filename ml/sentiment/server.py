"""BERT 情感推理服务。

独立部署，监听 5051 端口，供后端 Flask 业务调用。
接口: POST /predict  body: {"text": "..."}
返回: {"sentiment": 正向/负向/中性, "valence": -10~+10, "score": 0~1负面强度}

用法（在 ml 目录）：
    .venv\\Scripts\\python.exe sentiment\\server.py
"""
import os
import sys

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE = os.path.join(os.path.dirname(__file__), "..")
# 优先使用校园二次微调模型；不存在则回退公开数据模型
_CAMPUS = os.path.join(BASE, "data", "models", "sentiment_bert_campus")
_PUBLIC = os.path.join(BASE, "data", "models", "sentiment_bert")
MODEL_DIR = _CAMPUS if os.path.exists(os.path.join(_CAMPUS, "config.json")) else _PUBLIC

app = Flask(__name__)

tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    global tokenizer, model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    model.to(device)
    model.eval()
    print(f"模型已加载，设备: {device}")


def valence_from_logits(logits):
    """把二分类 logits 映射为 -10~+10 情感分值。

    正面概率高 -> 正值，负面概率高 -> 负值。
    """
    prob = torch.softmax(logits, dim=-1)[0]  # [负面概率, 正面概率]
    neg_p, pos_p = prob[0].item(), prob[1].item()
    valence = (pos_p - neg_p) * 10.0  # [-10, +10]
    return round(valence, 2)


# 高危自伤关键词（命中即紧急）
HIGH_RISK_WORDS = [
    "自杀", "想死", "结束生命", "轻生", "割腕", "活不下去", "了结",
    "伤害自己", "跳楼", "消失", "不想活", "自残",
]


def compute_emergency(text, sentiment, neg_p):
    """紧急程度：正常 / 关注 / 紧急。

    - 命中高危关键词 -> 紧急
    - 情感负面且强度高 -> 关注
    - 其余 -> 正常
    """
    for w in HIGH_RISK_WORDS:
        if w in text:
            return "紧急"
    if sentiment == "负向" and neg_p >= 0.85:
        return "关注"
    return "正常"


@app.post("/predict")
def predict():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is empty"}), 400

    inputs = tokenizer(text, truncation=True, padding=True, max_length=128, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
    prob = torch.softmax(logits, dim=-1)[0]
    neg_p, pos_p = prob[0].item(), prob[1].item()
    valence = valence_from_logits(logits)

    if neg_p > pos_p and neg_p > 0.55:
        sentiment = "负向"
        score = round(neg_p, 3)
    elif pos_p > neg_p and pos_p > 0.55:
        sentiment = "正向"
        score = 0.0
    else:
        sentiment = "中性"
        score = round(neg_p, 3)

    # 紧急程度判定：模型情感 + 高危关键词规则（后续可换为训练好的紧急分类头）
    emergency = compute_emergency(text, sentiment, neg_p)

    return jsonify({
        "sentiment": sentiment,
        "valence": valence,
        "score": score,
        "emergency": emergency,
        "prob_negative": round(neg_p, 4),
        "prob_positive": round(pos_p, 4),
    })


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5051, debug=False)
