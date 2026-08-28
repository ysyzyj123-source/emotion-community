# -*- coding: utf-8 -*-
"""快速验证微调后的 BERT 情感模型（不启动服务，直接加载推理）。"""
import os, sys, glob
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 模型可能在 data/models/sentiment_bert 下、也可能在子文件夹
cands = glob.glob(os.path.join(BASE, "data", "models", "sentiment_bert", "*"))
print("模型目录候选:", cands[:5])

# 找保存的模型目录
MODEL_DIR = os.path.join(BASE, "data", "models", "sentiment_bert")
if not os.path.exists(os.path.join(MODEL_DIR, "config.json")):
    # 可能是子文件夹
    sub = [d for d in cands if os.path.isdir(d) and os.path.exists(os.path.join(d, "config.json"))]
    if sub:
        MODEL_DIR = sub[0]
print("使用模型目录:", MODEL_DIR)

tok = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

tests = [
    "今天考研通过了，特别开心幸福！",
    "好难过，最近失眠又焦虑，感觉撑不住了",
    "我今天去食堂吃了顿饭",
    "室友关系让我很压抑想哭",
    "这次考试挂了，心情很低落",
]
for t in tests:
    inputs = tok(t, truncation=True, padding=True, max_length=128, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits
    prob = torch.softmax(logits, dim=-1)[0]
    neg_p, pos_p = prob[0].item(), prob[1].item()
    valence = (pos_p - neg_p) * 10
    label = "正向" if pos_p > neg_p else "负向"
    print(f"[{t}] -> {label} (正{pos_p:.3f} 负{neg_p:.3f}) valence={valence:+.1f}")
