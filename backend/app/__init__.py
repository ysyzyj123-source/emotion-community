"""应用工厂：创建 Flask 应用。"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from redis import Redis

from config import Config

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 全局 Redis 客户端
    app.redis = Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"],
        decode_responses=True,
    )

    # 注册蓝图
    from .api.auth import auth_bp
    from .api.user import user_bp
    from .api.post import post_bp
    from .api.reply import reply_bp
    from .api.warning import warning_bp
    from .api.admin import admin_bp
    from .api.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(post_bp, url_prefix="/api/post")
    app.register_blueprint(reply_bp, url_prefix="/api/reply")
    app.register_blueprint(warning_bp, url_prefix="/api/warning")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    # 创建数据表（开发阶段）
    with app.app_context():
        db.create_all()

    return app
