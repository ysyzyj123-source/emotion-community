"""预警记录模型。"""
from datetime import datetime
from .. import db


class WarningRecord(db.Model):
    """风险预警记录。"""
    __tablename__ = "warning"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    emergency = db.Column(db.String(16))  # 紧急等级：关注/紧急
    status = db.Column(db.Integer, default=0)  # 0=待处理 1=已处理 2=已下架
    handler = db.Column(db.Integer, db.ForeignKey("teacher.id"))  # 处理人
    handle_note = db.Column(db.Text)  # 处理记录
    handle_time = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
