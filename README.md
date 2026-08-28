# 大学生情感互助系统

面向高校校园场景的匿名情感互助社区平台。让每一次倾诉都被接住：
**匿名发布 → 情感识别与紧急判定 → 话题分流与智能标签 → 社区展示与互助回应 → 风险预警与老师跟进**。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React + Vite（PC 端响应式） |
| 后端 | Python Flask（RESTful API） |
| 数据库 | MySQL（业务）+ Redis（缓存） |
| 智能模型 | 微调 BERT（情感/紧急程度）+ LDA（话题分流） |

## 目录结构

```
代码/
├── backend/            # Flask 后端服务
│   ├── app/
│   │   ├── api/        # RESTful 路由（蓝图）
│   │   ├── models/     # SQLAlchemy 数据模型
│   │   ├── services/   # 业务逻辑层
│   │   └── utils/      # 工具/通用方法
│   ├── run.py          # 启动入口
│   ├── config.py       # 配置
│   └── requirements.txt
├── frontend/           # React 前端
│   ├── src/
│   │   ├── api/        # 后端接口封装
│   │   ├── components/ # 复用组件
│   │   ├── pages/      # 页面
│   │   ├── router/     # 路由
│   │   └── store/      # 全局状态
│   ├── vite.config.js
│   └── package.json
├── ml/                 # 模型训练与推理
│   ├── sentiment/      # BERT 情感分析（微调）
│   ├── topic/          # LDA 话题分流
│   └── data/           # 语料与模型权重
├── database/           # MySQL 建表与初始化脚本
├── docs/               # 部署 / 说明文档
└── scripts/            # 辅助脚本
```

## 快速开始（未完成占位）

> 依赖环境：Node.js 18+、Python 3.11+、MySQL 8、Redis。逐步搭建中。
