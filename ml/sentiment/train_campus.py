"""二次微调：用校园语料在已训练 BERT 基础上继续训练（增量更新）。

加载 data/models/sentiment_bert/（公开数据训练的主模型），
用校园语料 campus_train.jsonl 继续微调，让模型更懂校园表达。
"""
import os
import json

import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments,
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE, "data", "sentiment")
MODEL_DIR = os.path.join(BASE, "data", "models", "sentiment_bert")
OUT_DIR = os.path.join(BASE, "data", "models", "sentiment_bert_campus")

MAX_LEN = 128


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def make_dataset(rows, tokenizer):
    ds = Dataset.from_list(rows)
    ds = ds.map(lambda x: tokenizer(x["text"], truncation=True,
                                    padding="max_length", max_length=MAX_LEN), batched=True)
    ds.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    return ds


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    acc = accuracy_score(labels, preds)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f1}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

    train_rows = load_jsonl(os.path.join(DATA_DIR, "campus_train.jsonl"))
    val_rows = load_jsonl(os.path.join(DATA_DIR, "campus_val.jsonl"))

    train = make_dataset(train_rows, tokenizer)
    val = make_dataset(val_rows, tokenizer)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"设备: {device}, 校园语料二次微调")

    args = TrainingArguments(
        output_dir=os.path.join(OUT_DIR, "checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=3e-5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=20,
        report_to=[],
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=train, eval_dataset=val,
        compute_metrics=compute_metrics,
    )
    trainer.train()

    print("=== 二次微调后验证集评估 ===")
    for k, v in trainer.evaluate().items():
        print(f"  {k}: {v:.4f}")

    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)
    print(f"二次微调模型已保存到 {OUT_DIR}")


if __name__ == "__main__":
    main()
