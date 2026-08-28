"""JWT 鉴权辅助：从 token 解析当前用户身份。"""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def current_identity():
    """返回 (role, user_id)。需要请求已带 JWT。"""
    identity = get_jwt_identity()  # 形如 "role:id"
    if not identity:
        return None, None
    role, _, uid = identity.partition(":")
    try:
        return role, int(uid)
    except (ValueError, TypeError):
        return role, None


def login_required(fn):
    """要求登录（任意角色）。"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper
