# 大学生情感互助系统 - Flask 后端

## 运行（待环境就绪）

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## 目录

- `run.py` —— 启动入口
- `config.py` —— 配置（数据库、Redis、模型服务地址）
- `app/api` —— RESTful 路由（Blueprint）
- `app/models` —— SQLAlchemy ORM 模型
- `app/services` —— 业务逻辑
- `app/utils` —— 通用工具
