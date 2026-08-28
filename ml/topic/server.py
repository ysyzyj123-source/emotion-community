"""LDA 话题分流推理服务。

独立部署，监听 5052 端口。
接口: POST /predict body {"text": "..."}
返回: {"topic_label": 板块名, "prob": 最高主题概率, "topic_dist": {...}}

用法（在 ml 目录）：
    .venv\\Scripts\\python.exe topic\\server.py
"""
import os
import sys
import json

import jieba
from gensim import corpora
from gensim.models import LdaModel
from flask import Flask, request, jsonify

BASE = os.path.join(os.path.dirname(__file__), "..")
MODEL_DIR = os.path.join(BASE, "data", "models", "topic_lda")

app = Flask(__name__)
lda = None
dictionary = None
num_topics = 4

STOPWORDS = set(
    "的 了 是 在 和 我 你 他 她 它 也 都 就 很 要 会 能 不 有 好 想 这 那 怎么 什么 一个 今天 晚上 感觉 觉得 吗 啊 呀 吧 下 上 中 里 个 到 把 被 让 给 对 从 为 些 又 再 还 着 过 来 去 后 前 时候 现在 还是 这个".split()
)


def tokenize(text):
    return [w for w in jieba.lcut(text) if w.strip() and w not in STOPWORDS and len(w) > 1]


def load():
    global lda, dictionary, num_topics
    lda = LdaModel.load(os.path.join(MODEL_DIR, "lda.model"))
    dictionary = corpora.Dictionary.load(os.path.join(MODEL_DIR, "dictionary"))
    with open(os.path.join(MODEL_DIR, "topic_map.json"), encoding="utf-8") as f:
        meta = json.load(f)
    num_topics = meta.get("num_topics", 4)
    print(f"LDA 模型已加载: {num_topics} 主题")


# 主题代表词 -> 板块映射（根据训练后各主题代表性人工校准）
# 每个主题一个代表板块名，按训练输出主题序号对应
TOPIC_TO_CATEGORY = ["学业", "情感", "求职", "生活"]


@app.post("/predict")
def predict():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is empty"}), 400

    tokens = tokenize(text)
    bow = dictionary.doc2bow(tokens)
    if not bow:
        return jsonify({"topic_label": "生活", "category": "生活", "prob": 0.0, "topic_dist": {}})

    dist = lda[bow]
    dist = sorted(dist, key=lambda x: -x[1])
    top_topic, top_prob = dist[0]
    category = TOPIC_TO_CATEGORY[top_topic % len(TOPIC_TO_CATEGORY)]
    topic_dist = {str(t): float(round(p, 4)) for t, p in dist}
    return jsonify({
        "topic_label": category,
        "category": category,
        "prob": round(float(top_prob), 4),
        "topic_dist": topic_dist,
    })


if __name__ == "__main__":
    load()
    app.run(host="0.0.0.0", port=5052, debug=False)
