# 模型训练与推理模块
#
# 结构：
#   sentiment/   BERT 情感分析（微调 + 推理服务）
#   topic/       LDA 话题分流（训练 + 推理服务）
#   data/
#     raw/        原始语料
#     processed/  清洗后语料
#     models/     训练好的模型权重
#
# 两个推理服务独立部署（开题报告：模型服务与业务解耦）。
