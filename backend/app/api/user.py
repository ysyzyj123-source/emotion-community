"""用户路由：个人中心相关。"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..models import User, PointRecord
from ..utils.auth_util import current_identity

user_bp = Blueprint("user", __name__)


def _ok(data=None, msg="success", code=0):
    return jsonify({"code": code, "msg": msg, "data": data}), 200


@user_bp.get("/profile")
@jwt_required()
def profile():
    """当前用户公开信息：昵称、积分、等级。"""
    role, uid = current_identity()
    if role != "student":
        return _ok({"role": role, "name": "未知", "points": 0, "level": 1})

    user = User.query.get(uid)
    if not user:
        return _ok({"role": role, "name": "未知", "points": 0, "level": 1})

    return _ok({
        "user_id": user.id,
        "role": role,
        "name": user.nickname,
        "points": user.points or 0,
        "level": user.level or 1,
    })


@user_bp.get("/points/records")
@jwt_required()
def point_records():
    """当前用户的积分明细。"""
    role, uid = current_identity()
    if role != "student":
        return _ok({"items": []})

    records = PointRecord.query.filter_by(user_id=uid)\
        .order_by(PointRecord.create_time.desc()).all()
    items = [{
        "change": r.change,
        "action": r.action,
        "remark": r.remark,
        "create_time": r.create_time.strftime("%Y-%m-%d %H:%M") if r.create_time else None,
    } for r in records]
    return _ok({"items": items})
