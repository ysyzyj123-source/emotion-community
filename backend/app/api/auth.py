"""认证路由：注册、登录。

- 注册：仅普通学生（学号 + 昵称 + 密码），密码加密存储，学号唯一。
- 登录：三类角色（student/teacher/admin），按角色查对应表，校验密码，返回 JWT。
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import User, Teacher, Admin
from .. import db

auth_bp = Blueprint("auth", __name__)

# 角色 -> (对应模型, 登录主键字段, 显示名字段)
ROLE_MAP = {
    "student": (User, User.nickname, User.nickname),
    "teacher": (Teacher, Teacher.job_no, Teacher.name),
    "admin": (Admin, Admin.username, Admin.username),
}


def _ok(data=None, msg="success", code=0, http=200):
    return jsonify({"code": code, "msg": msg, "data": data}), http


def _fail(msg, code=1, http=400):
    return jsonify({"code": code, "msg": msg}), http


def _nickname_width(name):
    """计算昵称显示宽度：中日韩等宽字符按 2 计，其余按 1 计。"""
    width = 0
    for ch in name:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or 0x3000 <= cp <= 0x303F
                or 0xFF00 <= cp <= 0xFFEF or 0x3040 <= cp <= 0x30FF):
            width += 2
        else:
            width += 1
    return width


@auth_bp.post("/register")
def register():
    """学生注册：昵称 + 密码。"""
    data = request.get_json() or {}
    nickname = data.get("nickname", "").strip()
    password = data.get("password", "")

    # 字段校验
    if not nickname or not password:
        return _fail("昵称、密码不能为空")
    if _nickname_width(nickname) < 2:
        return _fail("昵称至少 2 个字符")
    if _nickname_width(nickname) > 12:
        return _fail("昵称最长 12 个字符（最多 6 个汉字）")
    if len(password) < 6:
        return _fail("密码长度至少 6 位")

    # 昵称唯一校验
    if User.query.filter_by(nickname=nickname).first():
        return _fail("该昵称已被使用", http=409)

    # 创建用户（密码加密）
    user = User(
        nickname=nickname,
        password=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return _ok({"user_id": user.id, "role": "student"}, "注册成功", http=201)


@auth_bp.post("/login")
def login():
    """三类角色统一登录。"""
    data = request.get_json() or {}
    account = data.get("account", "").strip()
    password = data.get("password", "")
    role = data.get("role", "student")

    if role not in ROLE_MAP:
        return _fail("角色不合法")
    if not account or not password:
        return _fail("账号或密码不能为空")

    model, id_field, name_field = ROLE_MAP[role]
    user = model.query.filter(id_field == account).first()

    # 统一提示：账号或密码错误（不暴露具体哪个错）
    if not user or not check_password_hash(user.password, password):
        return _fail("账号或密码错误")

    # 状态校验（学生可能被禁用）
    status = getattr(user, "status", 1)
    if status != 1:
        return _fail("该账号已被禁用，请联系管理员")

    display_name = getattr(user, name_field.key)
    identity = f"{role}:{user.id}"
    token = create_access_token(
        identity=identity,
        additional_claims={"role": role, "name": display_name},
    )
    return _ok({
        "token": token,
        "role": role,
        "name": display_name,
        "user_id": user.id,
    }, "登录成功")
