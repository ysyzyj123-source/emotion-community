"""用户基本概念路由（占位）。"""
from flask import Blueprint, jsonify

user_bp = Blueprint("user", __name__)


@user_bp.get("/profile")
def profile():
    """获取当前用户公开信息。"""
    return jsonify({"code": 0, "msg": "获取用户信息（占位实现）", "data": {}})
