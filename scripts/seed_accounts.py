"""初始账号种子脚本：创建老师和管理员演示账号。

用法（在 backend 目录下执行）：
    .venv\\Scripts\\python.exe scripts\\seed_accounts.py
"""
import sys, os
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app, db
from app.models import User, Teacher, Admin


def seed():
    app = create_app()
    with app.app_context():
        # 心理辅导老师
        if not Teacher.query.filter_by(job_no="T1001").first():
            db.session.add(Teacher(
                job_no="T1001", name="张老师",
                password=generate_password_hash("123456"), role="teacher",
            ))
            print("已创建老师 T1001 / 123456")

        # 系统管理员
        if not Admin.query.filter_by(username="admin").first():
            db.session.add(Admin(
                username="admin", password=generate_password_hash("admin123"),
            ))
            print("已创建管理员 admin / admin123")

        db.session.commit()
        print("种子账号完成")


if __name__ == "__main__":
    seed()
