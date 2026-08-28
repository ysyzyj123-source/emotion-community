"""重置 admin 演示账号密码为真实哈希。"""
import sys, os
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app, db
from app.models import Admin


def reset():
    app = create_app()
    with app.app_context():
        # 删除占位记录（PLACEHOLDER_HASH）
        Admin.query.filter_by(password="PLACEHOLDER_HASH").delete()
        # 确保存在正确密码的 admin
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            admin = Admin(username="admin", password=generate_password_hash("admin123"))
            db.session.add(admin)
        else:
            admin.password = generate_password_hash("admin123")
        db.session.commit()
        print("admin 密码已重置为 admin123")


if __name__ == "__main__":
    reset()
