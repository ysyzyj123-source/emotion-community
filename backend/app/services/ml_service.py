"""调用独立部署的模型服务（BERT 情感分析 / LDA 话题分流）。

优先级：优先调用真实模型服务；服务不可用时降级为关键词规则分析器，
保证功能链路不中断。模型服务部署后将自动切换到真实推理。
"""
import requests

from flask import current_app

from .rule_analyzer import analyze_sentiment as rule_sentiment
from .rule_analyzer import analyze_topic as rule_topic

# 模型服务请求超时
TIMEOUT = 5


def analyze_sentiment(text: str) -> dict:
    """情感分析，返回 {sentiment, emergency, score}。"""
    url = current_app.config.get("ML_SENTIMENT_URL")
    if url:
        try:
            resp = requests.post(url, json={"text": text}, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if data.get("sentiment"):
                return data
        except Exception:
            pass  # 服务不可用，走降级
    # 降级：关键词规则
    return rule_sentiment(text)


def analyze_topic(text: str) -> dict:
    """话题分流，返回 {topic_label, category}。"""
    url = current_app.config.get("ML_TOPIC_URL")
    if url:
        try:
            resp = requests.post(url, json={"text": text}, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if data.get("topic_label"):
                return data
        except Exception:
            pass  # 服务不可用，走降级
    # 降级：关键词规则
    return rule_topic(text)
