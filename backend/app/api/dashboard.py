"""数据看板：情感趋势、话题分布统计。

供心理辅导老师 / 管理员查看全局情绪走向与热点话题。
"""
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from .. import db
from ..models import SentimentResult, TopicResult, Post, Reply, User, Category
from ..utils.auth_util import current_identity

dashboard_bp = Blueprint("dashboard", __name__)


def _ok(data=None, msg="success", code=0):
    return jsonify({"code": code, "msg": msg, "data": data}), 200


def _fail(msg, code=1, http=400):
    return jsonify({"code": code, "msg": msg}), http


def _require_viewer():
    """看板允许心理辅导老师或管理员查看。"""
    role, uid = current_identity()
    if role in ("teacher", "admin"):
        return role
    return None


@dashboard_bp.get("/sentiment-trend")
@jwt_required()
def sentiment_trend():
    """情感趋势：每条帖子一个情感点，按发帖时间顺序排列。

    返回所有帖子（post 类型）的 {序号, 时间, 情感分值}，以及全部帖子
    的平均情感分值。前端用平滑曲线串起各点，并画出平均情感水平线。
    """
    if not _require_viewer():
        return _fail("仅心理辅导老师或管理员可查看", http=403)

    limit = request.args.get("limit", 50, type=int)
    limit = min(limit, 200)

    rows = (db.session.query(
                SentimentResult.target_id,
                SentimentResult.valence,
                SentimentResult.create_time)
            .filter(SentimentResult.target_type == "post")
            .order_by(SentimentResult.create_time.asc())
            .limit(limit)
            .all())

    points = []
    valence_values = []
    for idx, (target_id, valence, create_time) in enumerate(rows, start=1):
        v = valence if valence is not None else 0.0
        valence_values.append(v)
        points.append({
            "index": idx,
            "post_id": target_id,
            "time": create_time.strftime("%Y-%m-%d %H:%M") if create_time else None,
            "valence": round(v, 2),
        })

    avg_valence = round(sum(valence_values) / len(valence_values), 2) if valence_values else 0.0

    return _ok({
        "points": points,
        "avg": avg_valence,
        "min": -10,
        "max": 10,
    })


@dashboard_bp.get("/topic-distribution")
@jwt_required()
def topic_distribution():
    """话题分布：各板块的帖子数量。"""
    if not _require_viewer():
        return _fail("仅心理辅导老师或管理员可查看", http=403)

    rows = (db.session.query(Post.category_id, func.count().label("cnt"))
            .filter(Post.status == 1)
            .group_by(Post.category_id).all())

    cats = {c.id: c.name for c in Category.query.all()}
    labels, values = [], []
    for cat_id, cnt in rows:
        labels.append(cats.get(cat_id, "未知"))
        values.append(cnt)

    return _ok({"labels": labels, "values": values})


@dashboard_bp.get("/post-stats")
@jwt_required()
def post_stats():
    """帖子/回复/用户概览数字。"""
    if not _require_viewer():
        return _fail("仅心理辅导老师或管理员可查看", http=403)

    return _ok({
        "posts": Post.query.count(),
        "replies": Reply.query.count(),
        "users": User.query.count(),
    })
