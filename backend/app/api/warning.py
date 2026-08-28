"""心理辅导老师：预警工作台路由（占位）。"""
from flask import Blueprint, jsonify

warning_bp = Blueprint("warning", __name__)


@warning_bp.get("/list")
def list_warnings():
    """高风险预警列表（按紧急程度降序、可按时间段筛选）。"""
    return jsonify({"code": 0, "data": []}), 200


@warning_bp.get("/<int:warning_id>")
def get_warning(warning_id):
    """预警详情（帖子完整内容、情感分析结果、互助回复情况）。"""
    return jsonify({"code": 0, "data": {}}), 200


@warning_bp.post("/<int:warning_id>/handle")
def handle_warning(warning_id):
    """跟进处理：填写处理记录、标记处理状态。"""
    return jsonify({"code": 0, "msg": "处理成功（占位）"}), 200
