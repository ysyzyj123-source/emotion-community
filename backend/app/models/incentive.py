"""激励与反馈模型：积分、举报、反馈、通知。"""
from datetime import datetime
from .. import db


class PointRecord(db.Model):
    """积分记录。"""
    __tablename__ = "point_record"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    change = db.Column(db.Integer, nullable=False)  # 变动值
    action = db.Column(db.String(32))  # 行为类型：发帖/被回复/回复被采纳等
    remark = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    """举报。"""
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    target_type = db.Column(db.String(16))  # post/reply
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.Integer, default=0)  # 0=待处理 1=已处理
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Feedback(db.Model):
    """功能反馈。"""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(16))  # suggestion/bug
    content = db.Column(db.Text)
    status = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Notice(db.Model):
    """通知。"""
    __tablename__ = "notice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(500))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
