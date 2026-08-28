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
    """情感趋势：最近 N 天每天的正向/负向/中性帖子数量。"""
    if not _require_viewer():
        return _fail("仅心理辅导老师或管理员可查看", http=403)

    days = request.args.get("days", 7, type=int)
    days = min(days, 30)
    since = (datetime.utcnow() - timedelta(days=days - 1))
    since = since.replace(hour=0, minute=0, second=0, microsecond=0)

    rows = (db.session.query(
                func.date(SentimentResult.create_time).label("day"),
                SentimentResult.sentiment,
                func.count().label("cnt"))
            .filter(SentimentResult.target_type == "post",
                    SentimentResult.create_time >= since)
            .group_by("day", SentimentResult.sentiment)
            .all())

    data = {}
    for day, sentiment, cnt in rows:
        data.setdefault(str(day), {})[sentiment] = cnt

    labels, pos, neg, neu = [], [], [], []
    for i in range(days):
        d = (since + timedelta(days=i)).strftime("%Y-%m-%d")
        labels.append(d)
        bucket = data.get(d, {})
        pos.append(bucket.get("正向", 0))
        neg.append(bucket.get("负向", 0))
        neu.append(bucket.get("中性", 0))

    return _ok({"labels": labels, "正向": pos, "负向": neg, "中性": neu})


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
