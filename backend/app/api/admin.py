"""管理员路由：用户管理、内容审核、参数配置、系统监控（占位）。"""
from flask import Blueprint, jsonify

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
def list_users():
    return jsonify({"code": 0, "data": []}), 200


@admin_bp.get("/posts/audit")
def audit_posts():
    return jsonify({"code": 0, "data": []}), 200


@admin_bp.get("/config/points")
def get_points_config():
    return jsonify({"code": 0, "data": {}}), 200


@admin_bp.get("/stats/board")
def stats_board():
    """数据统计看板。"""
    return jsonify({"code": 0, "data": {}}), 200
