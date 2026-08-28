"""用户相关模型：普通用户、心理辅导老师、系统管理员。"""
from datetime import datetime
from .. import db


class User(db.Model):
    """普通学生（匿名主体）。"""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_no = db.Column(db.String(32), unique=True, nullable=True)  # 学号（可选）
    nickname = db.Column(db.String(64), unique=True, nullable=False)  # 昵称（唯一，登录标识）
    password = db.Column(db.String(255), nullable=False)  # 加密存储（scrypt 哈希较长）
    avatar = db.Column(db.String(255))
    anonymous = db.Column(db.Boolean, default=True)  # 匿名标识
    points = db.Column(db.Integer, default=0)  # 积分
    level = db.Column(db.Integer, default=1)  # 等级
    status = db.Column(db.Integer, default=1)  # 状态，1=正常 0=禁用
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间


class Teacher(db.Model):
    """心理辅导老师。"""
    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_no = db.Column(db.String(32), unique=True, nullable=False)  # 工号
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(16), default="teacher")
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(db.Model):
    """系统管理员。"""
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
