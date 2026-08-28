"""帖子路由：发帖（触发智能流水线）、浏览、详情。"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Post, Category, SentimentResult, TopicResult, WarningRecord
from ..services.ml_service import analyze_sentiment, analyze_topic
from ..services.point_service import add_points
from ..utils.auth_util import current_identity
from ..models.user import User

post_bp = Blueprint("post", __name__)


def _ok(data=None, msg="success", code=0, http=200):
    return jsonify({"code": code, "msg": msg, "data": data}), http


def _fail(msg, code=1, http=400):
    return jsonify({"code": code, "msg": msg}), http


def _category_id_by_name(name):
    cat = Category.query.filter_by(name=name).first()
    return cat.id if cat else None


@post_bp.post("")
@jwt_required()
def create_post():
    """发帖：同步触发情感分析 + 话题分流，高危内容生成预警记录。"""
    role, uid = current_identity()
    if role != "student":
        return _fail("仅学生可发帖", http=403)

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return _fail("标题和正文不能为空")
    if len(title) > 50:
        return _fail("标题最长 50 字")

    # 智能分析
    senti = analyze_sentiment(content)
    topic = analyze_topic(content)
    category_id = _category_id_by_name(topic.get("category", "生活"))
    if category_id is None:
        category_id = _category_id_by_name("生活")

    post = Post(
        category_id=category_id,
        user_id=uid,
        title=title,
        content=content,
        sentiment_label=senti.get("sentiment"),
        emergency=senti.get("emergency"),
        category_label=topic.get("topic_label"),
    )
    db.session.add(post)
    db.session.flush()  # 获取 post.id

    # 写入情感分析结果
    db.session.add(SentimentResult(
        target_id=post.id, target_type="post",
        sentiment=senti.get("sentiment"),
        emergency=senti.get("emergency"),
        score=senti.get("score", 0.0),
    ))
    # 写入话题分析结果
    db.session.add(TopicResult(
        post_id=post.id,
        topic_label=topic.get("topic_label"),
        category_id=category_id,
    ))

    # 高危 -> 生成预警记录
    warning_created = False
    if senti.get("emergency") in ("关注", "紧急"):
        db.session.add(WarningRecord(
            post_id=post.id,
            emergency=senti.get("emergency"),
            status=0,
        ))
        warning_created = True

    # 发帖积分：发布者 +5
    add_points(uid, "post", f"发布帖子 #{post.id}")

    db.session.commit()
    return _ok({
        "post_id": post.id,
        "sentiment": post.sentiment_label,
        "emergency": post.emergency,
        "category": topic.get("category"),
        "topic_label": topic.get("topic_label"),
        "warning": warning_created,
        "points_gained": 5,
    }, "发布成功", http=201)


@post_bp.get("/list")
@jwt_required()
def list_posts():
    """帖子列表（按板块过滤 + 分页）。"""
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    per_page = min(per_page, 50)

    query = Post.query.filter(Post.status == 1)
    if category_id:
        query = query.filter(Post.category_id == category_id)
    query = query.order_by(Post.create_time.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [{
        "post_id": p.id,
        "title": p.title,
        "content": p.content[:80],  # 列表只展示摘要
        "category_id": p.category_id,
        "sentiment": p.sentiment_label,
        "emergency": p.emergency,
        "create_time": p.create_time.strftime("%Y-%m-%d %H:%M") if p.create_time else None,
    } for p in pagination.items]

    return _ok({
        "items": items,
        "page": page,
        "total": pagination.total,
        "pages": pagination.pages,
    })


@post_bp.get("/<int:post_id>")
@jwt_required()
def get_post(post_id):
    """帖子详情（含情感标签、话题、预警状态）。"""
    post = Post.query.get(post_id)
    if not post or post.status != 1:
        return _fail("帖子不存在或已下架", http=404)

    senti = SentimentResult.query.filter_by(
        target_id=post.id, target_type="post").first()
    topi = TopicResult.query.filter_by(post_id=post.id).first()
    warning = WarningRecord.query.filter_by(post_id=post.id).first()

    author = User.query.get(post.user_id)
    return _ok({
        "post_id": post.id,
        "title": post.title,
        "content": post.content,
        "category_id": post.category_id,
        "category": Category.query.get(post.category_id).name if post.category_id else None,
        "author_nickname": author.nickname if author else "匿名",
        "sentiment": post.sentiment_label,
        "emergency": post.emergency,
        "topic_label": topi.topic_label if topi else None,
        "is_warning": warning is not None,
        "warning_emergency": warning.emergency if warning else None,
        "create_time": post.create_time.strftime("%Y-%m-%d %H:%M") if post.create_time else None,
    })


@post_bp.get("/categories")
@jwt_required()
def list_categories():
    """板块列表。"""
    cats = Category.query.filter_by(status=1).order_by(Category.sort).all()
    return _ok([{"id": c.id, "name": c.name, "description": c.description} for c in cats])
