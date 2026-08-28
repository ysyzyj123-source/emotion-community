"""回复路由：回复帖子（情感检测，攻击性内容拦截），写入积分。"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Post, Reply, SentimentResult
from ..services.ml_service import analyze_sentiment
from ..services.point_service import add_points
from ..utils.auth_util import current_identity

reply_bp = Blueprint("reply", __name__)


def _ok(data=None, msg="success", code=0, http=200):
    return jsonify({"code": code, "msg": msg, "data": data}), http


def _fail(msg, code=1, http=400):
    return jsonify({"code": code, "msg": msg}), http


@reply_bp.post("/<int:post_id>")
@jwt_required()
def create_reply(post_id):
    """回复：情感检测（友善/攻击），有效回复双方获得积分。"""
    role, uid = current_identity()
    if role != "student":
        return _fail("仅学生可回复", http=403)

    post = Post.query.get(post_id)
    if not post or post.status != 1:
        return _fail("帖子不存在或已下架", http=404)

    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return _fail("回复内容不能为空")

    # 情感检测：检出攻击倾向则拦截
    senti = analyze_sentiment(content)
    if senti.get("sentiment") == "负向" and senti.get("score", 0) >= 0.7:
        return _fail("请保持友善沟通，当前回复内容可能存在攻击性", http=400)

    reply = Reply(
        post_id=post_id,
        user_id=uid,
        content=content,
        result=senti.get("sentiment"),
    )
    db.session.add(reply)
    db.session.flush()  # 取 reply.id

    # 写情感分析结果
    db.session.add(SentimentResult(
        target_id=reply.id, target_type="reply",
        sentiment=senti.get("sentiment"),
        emergency=senti.get("emergency"),
        score=senti.get("score", 0.0),
    ))

    # 积分：回复者 +2；帖子楼主被回复 +3（自己回复自己不重复加）
    reply_points = add_points(uid, "reply", f"回复帖子 #{post_id}")
    author_points = 0
    if post.user_id != uid:
        author_points = add_points(post.user_id, "post_replied", f"帖子 #{post_id} 收到回复")

    db.session.commit()
    return _ok({
        "reply_id": reply.id,
        "result": reply.result,
        "reply_points": reply_points,
        "author_points": author_points,
    }, "回复成功", http=201)


@reply_bp.get("/post/<int:post_id>")
@jwt_required()
def list_replies(post_id):
    """某个帖子的回复列表。"""
    replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.create_time.asc()).all()
    from ..models.user import User
    items = []
    for r in replies:
        author = User.query.get(r.user_id)
        items.append({
            "reply_id": r.id,
            "content": r.content,
            "result": r.result,
            "adopted": r.adopted,
            "like_count": r.like_count,
            "author_nickname": author.nickname if author else "匿名",
            "create_time": r.create_time.strftime("%Y-%m-%d %H:%M") if r.create_time else None,
        })
    return _ok({"items": items})
