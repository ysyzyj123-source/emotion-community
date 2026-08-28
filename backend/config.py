"""项目配置。可通过环境变量覆盖，便于部署。"""
import os
from datetime import timedelta

from dotenv import load_dotenv

# 加载 backend 目录下的 .env（若存在）
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class Config:
    # === 基础 ===
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    # === MySQL ===
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DB = os.getenv("MYSQL_DB", "emotion_community")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # === Redis ===
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    # === JWT ===
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # === 模型服务 ===
    # 情感分析 / 话题分流服务独立部署，通过 HTTP 调用
    ML_SENTIMENT_URL = os.getenv("ML_SENTIMENT_URL", "http://127.0.0.1:5051/predict")
    ML_TOPIC_URL = os.getenv("ML_TOPIC_URL", "http://127.0.0.1:5052/predict")

    # === 业务参数（开题报告中的默认值）===
    # 预警阈值：score >= theta 判定高风险
    WARNING_THETA = float(os.getenv("WARNING_THETA", "0.6"))
    # 情感分析异步任务队列名
    TASK_QUEUE = os.getenv("TASK_QUEUE", "ml_pipeline")
