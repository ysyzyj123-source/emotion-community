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

    # 规则兜底：命中高危自伤关键词则强制判紧急（保证高危不遗漏）
    if HIGH_RISK_WORDS and any(w in text for w in HIGH_RISK_WORDS):
        emg_idx = 2  # 紧急
        valence = min(valence, -8.0)  # 高危同时压低情感分值

    return jsonify({
        "sentiment": SENT_LABELS[sent_idx],
        "emergency": EMG_LABELS[emg_idx],
        "valence": round(float(valence), 2),
        "sentiment_probs": {SENT_LABELS[i]: round(float(sent_probs[i]), 4) for i in range(3)},
        "emergency_probs": {EMG_LABELS[i]: round(float(emg_probs[i]), 4) for i in range(3)},
    })


# 高危自伤关键词（规则兜底，命中即紧急）
HIGH_RISK_WORDS = [
    "自杀", "想死", "结束生命", "轻生", "割腕", "活不下去", "了结",
    "伤害自己", "跳楼", "消失", "不想活", "自残", "自我了结", "想不开",
]


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5051, debug=False)
