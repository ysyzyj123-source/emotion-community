"""回复路由（占位）。"""
from flask import Blueprint, request, jsonify

reply_bp = Blueprint("reply", __name__)


@reply_bp.post("/<int:post_id>")
def create_reply(post_id):
    """回复：情感检测（友善/攻击），有效回复触发积分。"""
    data = request.get_json() or {}
    return jsonify({"code": 0, "msg": "回复成功（占位）"}), 201
