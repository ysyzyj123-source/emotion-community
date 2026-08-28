"""多任务 BERT 训练脚本（情感 + 紧急 + 分值，三头共享编码）。

用法：
    .venv\\Scripts\\python.exe sentiment\\train_multitask.py

模型：bert-base-chinese + MultiTaskBert 三任务头
数据：data/sentiment/multitask_{train,val}.jsonl（text, sentiment, emergency, valence）
"""
import os
import json

import torch
from transformers import BertConfig, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score

from model import MultiTaskBert

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE, "data", "sentiment")
OUT_DIR = os.path.join(BASE, "data", "models", "multitask_bert")
MODEL_NAME = "bert-base-chinese"
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
    ds = ds.map(lambda x: {
        "labels": x["sentiment"],
        "emergency_labels": x["emergency"],
        "valence_labels": x["valence"],
    })
    ds.set_format("torch", columns=["input_ids", "attention_mask",
                                    "labels", "emergency_labels", "valence_labels"])
    return ds


def separate_compute_metrics(pred):
    # Trainer 的 compute_metrics 接收 (logits, labels)，但多任务需自定义后处理。
    # 这里用简单方式：预测从 eval_pred 的 predictions 结构中取（由 MultiTaskTrainer 提供）
    return {}


def main():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    config = BertConfig.from_pretrained(MODEL_NAME)
    model = MultiTaskBert.from_pretrained(MODEL_NAME, config=config)

    train_rows = load_jsonl(os.path.join(DATA_DIR, "multitask_train.jsonl"))
    val_rows = load_jsonl(os.path.join(DATA_DIR, "multitask_val.jsonl"))
    train = make_dataset(train_rows, tokenizer)
    val = make_dataset(val_rows, tokenizer)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"设备: {device}, 多任务训练: 情感/紧急/分值")

    os.makedirs(OUT_DIR, exist_ok=True)
    args = TrainingArguments(
        output_dir=os.path.join(OUT_DIR, "checkpoints"),
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        learning_rate=2e-5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_steps=50,
        report_to=[],
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=train, eval_dataset=val,
    )
    trainer.train()

    print("=== 多任务模型验证 ===")
    eval_metrics = trainer.evaluate()
    for k, v in eval_metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)
    print(f"多任务模型已保存到 {OUT_DIR}")


if __name__ == "__main__":
    main()
