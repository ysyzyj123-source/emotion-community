"""积分服务：统一处理积分变更，可复用、便于后续做成管理员可配置规则。

积分规则（开题报告 4.3 节）：
  - 发布求助帖        +5
  - 回复他人（有效）   +2
  - 回复被楼主采纳     +8
  - 回复获得点赞       +3
  - 帖子被回复         +3（楼主收到反馈）
"""
from datetime import datetime

from .. import db
from ..models.incentive import PointRecord
from ..models.user import User

# 积分规则表（后续可改为数据库配置，由管理员动态调整）
RULES = {
    "post": 5,          # 发帖
    "reply": 2,         # 有效回复他人
    "adopted": 8,       # 回复被采纳
    "reply_liked": 3,   # 回复被点赞
    "post_replied": 3,  # 帖子被回复（楼主）
}

LEVEL_STEP = 20  # 每 20 分升一级


def add_points(user_id: int, action: str, remark: str = "") -> int:
    """给用户加分并记录。返回变动值（0 表示该 action 无积分或不生效）。"""
    points = RULES.get(action, 0)
    if points <= 0:
        return 0

    user = User.query.get(user_id)
    if not user:
        return 0

    user.points = (user.points or 0) + points
    user.level = user.points // LEVEL_STEP + 1

    db.session.add(PointRecord(
        user_id=user_id,
        change=points,
        action=action,
        remark=remark,
    ))
    db.session.flush()
    return points


def level_of(points: int) -> int:
    return points // LEVEL_STEP + 1
