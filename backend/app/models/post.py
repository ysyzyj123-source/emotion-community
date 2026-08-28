"""社区相关内容模型：板块、帖子、回复、收藏。"""
from datetime import datetime
from .. import db


class Category(db.Model):
    """板块：学业、情感、求职、生活。"""
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(255))
    sort = db.Column(db.Integer, default=0)  # 排序
    status = db.Column(db.Integer, default=1)


class Post(db.Model):
    """帖子。"""
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sentiment_label = db.Column(db.String(16))  # 情绪标签：正向/负向
    emergency = db.Column(db.String(16))  # 紧急程度：正常/关注/紧急
    category_label = db.Column(db.String(32))  # LDA 话题标签
    status = db.Column(db.Integer, default=1)  # 1=正常 0=下架
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Reply(db.Model):
    """回复。"""
    __tablename__ = "reply"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(16))  # 情绪检测（友善/攻击）
    adopted = db.Column(db.Boolean, default=False)  # 是否被楼主采纳
    like_count = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Collect(db.Model):
    """收藏（普通用户 <-> 帖子 多对多）。"""
    __tablename__ = "collect"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "post_id", name="uq_collect"),)
