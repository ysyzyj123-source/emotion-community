"""心理辅导老师：预警工作台。

功能：查看高风险预警列表、预警详情、跟进处理（填处理记录/标记状态/下架）。
"""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from .. import db
from ..models import WarningRecord, Post, Teacher
from ..utils.auth_util import current_identity

warning_bp = Blueprint("warning", __name__)


def _ok(data=None, msg="success", code=0):
    return jsonify({"code": code, "msg": msg, "data": data}), 200


def _fail(msg, code=1, http=400):
    return jsonify({"code": code, "msg": msg}), http


def _require_teacher():
    """校验当前用户是心理辅导老师，否则拒绝。返回 teacher_id。"""
    role, uid = current_identity()
    if role != "teacher":
        return None
    return uid


@warning_bp.get("/list")
@jwt_required()
def list_warnings():
    """高风险预警列表（按紧急程度、状态排序，可按状态筛选）。"""
    teacher_id = _require_teacher()
    if not teacher_id:
        return _fail("仅心理辅导老师可访问预警工作台", http=403)

    status = request.args.get("status", type=int)  # 0待处理 1已处理 2已下架
    query = WarningRecord.query
    if status is not None:
        query = query.filter(WarningRecord.status == status)

    # 紧急优先 -> 未处理优先 -> 最新在前
    query = query.order_by(
        WarningRecord.status.asc(),
        WarningRecord.create_time.desc(),
    ).all()

    items = []
    for w in query:
        post = Post.query.get(w.post_id)
        items.append({
            "warning_id": w.id,
            "post_id": w.post_id,
            "title": post.title if post else "",
            "content": (post.content[:60] if post else ""),
            "emergency": w.emergency,
            "status": w.status,
            "create_time": w.create_time.strftime("%Y-%m-%d %H:%M") if w.create_time else None,
        })
    return _ok({"items": items})


@warning_bp.get("/stats")
@jwt_required()
def stats():
    """预警统计：供工作台顶部概览。"""
    teacher_id = _require_teacher()
    if not teacher_id:
        return _fail("仅心理辅导老师可访问", http=403)

    total = WarningRecord.query.count()
    pending = WarningRecord.query.filter_by(status=0).count()
    handled = WarningRecord.query.filter_by(status=1).count()
    taken_down = WarningRecord.query.filter_by(status=2).count()
    return _ok({
        "total": total,
        "pending": pending,
        "handled": handled,
        "taken_down": taken_down,
    })


@warning_bp.get("/<int:warning_id>")
@jwt_required()
def get_warning(warning_id):
    """预警详情：帖子完整内容、情感分析结果、回复情况。"""
    teacher_id = _require_teacher()
    if not teacher_id:
        return _fail("仅心理辅导老师可访问", http=403)

    w = WarningRecord.query.get(warning_id)
    if not w:
        return _fail("预警记录不存在", http=404)

    post = Post.query.get(w.post_id)
    # 情感分析结果
    from ..models import SentimentResult, Reply
    senti = SentimentResult.query.filter_by(
        target_id=w.post_id, target_type="post").first()
    replies = Reply.query.filter_by(post_id=w.post_id)\
        .order_by(Reply.create_time.asc()).all()

    return _ok({
        "warning_id": w.id,
        "status": w.status,
        "emergency": w.emergency,
        "handle_note": w.handle_note,
        "handle_time": w.handle_time.strftime("%Y-%m-%d %H:%M") if w.handle_time else None,
        "create_time": w.create_time.strftime("%Y-%m-%d %H:%M") if w.create_time else None,
        "post": {
            "title": post.title if post else "",
            "content": post.content if post else "",
            "sentiment": senti.sentiment if senti else None,
            "emergency": senti.emergency if senti else None,
            "score": senti.score if senti else None,
        } if post else None,
        "replies": [{"content": r.content, "author_id": r.user_id} for r in replies],
    })


@warning_bp.post("/<int:warning_id>/handle")
@jwt_required()
def handle_warning(warning_id):
    """跟进处理：填写处理记录 + 标记状态。"""
    teacher_id = _require_teacher()
    if not teacher_id:
        return _fail("仅心理辅导老师可访问", http=403)

    w = WarningRecord.query.get(warning_id)
    if not w:
        return _fail("预警记录不存在", http=404)

    data = request.get_json() or {}
    note = (data.get("note") or "").strip()
    status = data.get("status", 1)  # 1=已处理 2=已下架

    if status not in (1, 2):
        return _fail("状态不合法")
    if not note:
        return _fail("请填写处理记录")

    w.status = status
    w.handle_note = note
    w.handler = teacher_id
    w.handle_time = datetime.now()

    # 若下架则同步把帖子下架
    if status == 2:
        post = Post.query.get(w.post_id)
        if post:
            post.status = 0

    db.session.commit()
    return _ok({"warning_id": w.id, "status": w.status}, "处理成功")
