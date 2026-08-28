"""训练 LDA 主题模型（轻量、内存安全版）。

流程：
  1. 读取教育语料 corpus.jsonl
  2. jieba 分词 + 去停用词
  3. 训练 LDA（固定 4 主题，对应学业/情感/求职/生活）
  4. 保存模型与词典、主题->板块映射

输出：data/models/topic_lda/{lda.model, dictionary, topic_map.json}
说明：采用固定 4 主题 + 低 passes，避免 c_v 一致性计算和大内存开销。
"""
import os
import json

import jieba
from gensim import corpora
from gensim.models import LdaModel

BASE = os.path.join(os.path.dirname(__file__), "..")
CORPUS_PATH = os.path.join(BASE, "data", "topic", "corpus.jsonl")
OUT_DIR = os.path.join(BASE, "data", "models", "topic_lda")
os.makedirs(OUT_DIR, exist_ok=True)

# 主题 -> 板块映射（按板块名）
CATEGORY_NAMES = ["学业", "情感", "求职", "生活"]

# 停用词
STOPWORDS = set(
    "的 了 是 在 和 我 你 他 她 它 也 都 就 很 要 会 能 不 有 好 想 这 那 怎么 什么 一个 今天 晚上 感觉 觉得 吗 啊 呀 吧 下 上 中 里 个 到 把 被 让 给 对 从 为 些 又 再 还 着 过 来 去 后 前 时候 现在 还是 这个".split()
)


def tokenize(text):
    words = jieba.lcut(text)
    return [w for w in words if w.strip() and w not in STOPWORDS and len(w) > 1]


def load_corpus():
    docs = []
    with open(CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def main():
    docs = load_corpus()
    texts = [d["text"] for d in docs]
    tokenized = [tokenize(t) for t in texts]
    tokenized = [t for t in tokenized if len(t) > 2]  # 过滤太短的
    print(f"语料 {len(texts)} 条 -> 有效文档 {len(tokenized)} 条")

    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=2, no_above=0.6)
    corpus = [dictionary.doc2bow(t) for t in tokenized]
    print(f"词典大小: {len(dictionary)}, 语料词袋: {len(corpus)}")

    # 场景 A：确定性4主题（对应学业/情感/求职/生活），轻量不爆内存
    print("=== 训练 LDA 主题模型（固定 4 主题）===")
    lda = LdaModel(
        corpus, num_topics=4, id2word=dictionary,
        passes=8, random_state=42,  # 不启用 alpha/eta="auto"，避免额外内存
    )

    # 保存
    lda.save(os.path.join(OUT_DIR, "lda.model"))
    dictionary.save(os.path.join(OUT_DIR, "dictionary"))
    print("模型与词典已保存")

    # 输出每个主题的代表词
    print("=== 各主题代表词 ===")
    for tid, topic in lda.print_topics(num_topics=4, num_words=10):
        print(f" 主题{tid}: {topic}")

    # 保存主题->板块映射（供推理服务用）
    with open(os.path.join(OUT_DIR, "topic_map.json"), "w", encoding="utf-8") as f:
        json.dump({"num_topics": 4, "categories": CATEGORY_NAMES}, f, ensure_ascii=False)
    print("映射已保存")


if __name__ == "__main__":
    main()
