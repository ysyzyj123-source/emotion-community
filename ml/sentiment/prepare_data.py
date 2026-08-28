"""准备中文情感二分类数据集（ChnSentiCorp）。

直接从 huggingface datasets 加载，或用本地 csv。
输出训练/验证/测试三份 JSONL：每条 {text, label}，label: 0=负面 1=正面。
说明：ChnSentiCorp 是公开冷链情感数据集（正/负二分类），
用于训练 BERT 情感倾向主模型；紧急程度后续独立补充语料。
"""
import os
import json
import csv

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sentiment")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_chnsenticorp():
    """尝试用 datasets 库加载 ChnSentiCorp。"""
    try:
        from datasets import load_dataset
        ds = load_dataset("lansinuote/ChnSentiCorp")
        return ds
    except Exception as e:
        print(f"[datasets 加载失败: {e}]，尝试本地 csv")
        return None


def local_csv_run(csv_path):
    """从本地 csv 读取（列: label, review）。0 负面 / 1 正面。"""
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            label = int(r["label"])
            text = r["review"].strip()
            if text:
                rows.append({"text": text, "label": label})
    return rows


def split_data(rows):
    """简单划分（80/10/10）。这里保持顺序，实际用 sklearn 更好。"""
    from sklearn.model_selection import train_test_split
    train, temp = train_test_split(rows, test_size=0.2, random_state=42, stratify=[r["label"] for r in rows])
    val, test = train_test_split(temp, test_size=0.5, random_state=42, stratify=[r["label"] for r in temp])
    return train, val, test


def save_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ds = load_chnsenticorp()
    rows = []
    if ds is not None:
        # 合并 train/test
        all_rows = []
        for split in ["train", "test"]:
            for item in ds[split]:
                all_rows.append({"text": item["text"], "label": int(item["label"])})
        rows = all_rows
        print(f"[datasets] 加载 {len(rows)} 条")
    else:
        csv_path = os.path.join(RAW_DIR, "ChnSentiCorp.csv")
        if not os.path.exists(csv_path):
            print(f"未找到本地数据 {csv_path}，请手动放置（列: label, review）")
            return
        rows = local_csv_run(csv_path)
        print(f"[本地csv] 加载 {len(rows)} 条")

    train, val, test = split_data(rows)
    save_jsonl(os.path.join(PROCESSED_DIR, "train.jsonl"), train)
    save_jsonl(os.path.join(PROCESSED_DIR, "val.jsonl"), val)
    save_jsonl(os.path.join(PROCESSED_DIR, "test.jsonl"), test)
    print(f"已保存 train={len(train)} val={len(val)} test={len(test)}")


if __name__ == "__main__":
    main()
