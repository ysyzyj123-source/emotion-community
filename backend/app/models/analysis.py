"""分析结果模型：情感分析结果、话题分析结果。"""
from datetime import datetime
from .. import db


class SentimentResult(db.Model):
    """情感分析结果（主键、目标ID、目标类型、情绪倾向、紧急程度、负面评分）。"""
    __tablename__ = "sentiment_result"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target_id = db.Column(db.Integer, nullable=False)  # 关联帖子或回复
    target_type = db.Column(db.String(16), nullable=False)  # post/reply
    sentiment = db.Column(db.String(16))  # 情感倾向：正向/负向
    emergency = db.Column(db.String(16))  # 紧急程度：正常/关注/紧急
    score = db.Column(db.Float, default=0.0)  # 负面强度评分 s
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class TopicResult(db.Model):
    """话题分析结果（LDA 分流出的板块与标签）。"""
    __tablename__ = "topic_result"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    topic_label = db.Column(db.String(32))  # 话题标签
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))  # 所属板块
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
