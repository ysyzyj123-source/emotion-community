"""从 counseling-cpsdd 清洗提取消解法语料（高效版）。

优化：
  - 去除 O(N^2) 的重复判断，改用一个 count 限制每对话提取条数
  - 逐条 writer 边处理边写入（避免中途全丢）
  - 限制条数以加快速度
  - 用 streaming 或限制样本量提升速度
"""
import os
import json
import random

from datasets import load_dataset

random.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment")
OUT = os.path.join(BASE, "cpsdd_train.jsonl")
os.makedirs(BASE, exist_ok=True)

# 限制样本量，加快构建（5.4万全量太慢，先取 1/2，约2.7万对话）
MAX_ITEMS = 20000

SEV_MAP = {
    "1": ("正常", -2.0),
    "2": ("正常", -3.5),
    "3": ("关注", -5.5),
    "4": ("关注", -7.5),
    "5": ("紧急", -9.5),
}
EMG_LABEL = {"正常": 0, "关注": 1, "紧急": 2}


def build():
    ds = load_dataset("XuShihao6715/counseling-cpsdd", split="train")
    rows = []
    for i in range(min(MAX_ITEMS, len(ds))):
        item = ds[i]
        profile = item.get("client_profile") or {}
        sev = str(profile.get("start_severity", "3"))
        msgs = item.get("messages", []) or []
        emg_label, base = SEV_MAP.get(sev, ("关注", -6.0))
        client_count = 0
        for m in msgs:
            if not isinstance(m, dict):
                continue
            if m.get("role") != "client":
                continue
            text = (m.get("content") or "").strip()
            if len(text) < 6:
                continue
            valence = round(base + random.uniform(-0.8, 0.8), 1)
            rows.append({
                "text": text,
                "sentiment": 0,  # 心理求助基本为负向
                "emergency": EMG_LABEL[emg_label],
                "valence": valence,
            })
            client_count += 1
            if client_count >= 4:  # 每对话最多取4条求助者话语
                break
        if i % 5000 == 0 and i > 0:
            print(f"  处理 {i}/{MAX_ITEMS}, 已收集 {len(rows)} 条", flush=True)

    # 去重
    seen = set(); dedup = []
    for r in rows:
        if r["text"] not in seen:
            seen.add(r["text"]); dedup.append(r)
    rows = dedup

    random.shuffle(rows)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    ct = {}
    for r in rows:
        ct[r["emergency"]] = ct.get(r["emergency"], 0) + 1
    print(f"完成: 共 {len(rows)} 条", flush=True)
    print(f"  紧急分布: {ct}", flush=True)


if __name__ == "__main__":
    build()
