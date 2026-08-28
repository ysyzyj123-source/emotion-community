"""微调 BERT 中文情感模型（情感倾向二分类）。

用法（在 ml 目录，用 ml/.venv 的 python 执行）：
    .venv\\Scripts\\python.exe sentiment\\train.py

模型：bert-base-chinese（中文预训练 BERT）
任务：情感二分类，label 0=负面 1=正面
输出：微调后的模型保存到 data/models/sentiment_bert/
"""
import os
import json
import glob

import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments,
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

BASE = os.path.join(os.path.dirname(__file__), "..")
PROCESSED_DIR = os.path.join(BASE, "data", "sentiment", "processed")
MODEL_DIR = os.path.join(BASE, "data", "models", "sentiment_bert")

MODEL_NAME = "bert-base-chinese"  # 中文预训练 BERT
MAX_LEN = 128
NUM_LABELS = 2  # 0 负面 / 1 正面


def load_dataset_split(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return Dataset.from_list(rows)


def tokenize(examples, tokenizer):
    return tokenizer(
        examples["text"], truncation=True, padding="max_length",
        max_length=MAX_LEN,
    )


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    acc = accuracy_score(labels, preds)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f1}


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=NUM_LABELS)

    train = load_dataset_split(os.path.join(PROCESSED_DIR, "train.jsonl"))
    val = load_dataset_split(os.path.join(PROCESSED_DIR, "val.jsonl"))
    test = load_dataset_split(os.path.join(PROCESSED_DIR, "test.jsonl"))

    train = train.map(lambda x: tokenize(x, tokenizer), batched=True)
    val = val.map(lambda x: tokenize(x, tokenizer), batched=True)
    test = test.map(lambda x: tokenize(x, tokenizer), batched=True)

    train.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    val.set_format("torch", columns=["input_ids", "attention_mask", "label"])
    test.set_format("torch", columns=["input_ids", "attention_mask", "label"])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"使用设备: {device}")

    args = TrainingArguments(
        output_dir=os.path.join(MODEL_DIR, "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=50,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train,
        eval_dataset=val,
        compute_metrics=compute_metrics,
    )
    trainer.train()

    # 在测试集评估
    print("=== 测试集评估 ===")
    metrics = trainer.evaluate(test)
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    # 保存最终模型
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"模型已保存到 {MODEL_DIR}")


if __name__ == "__main__":
    main()
