"""多任务 BERT 情感分析模型（大模型式结构：共享编码器 + 三任务头）。

结构：
  [CLS]向量 h
    ├── 任务头1：情感倾向分类（0负/1正/2中性）  num_labels=3
    ├── 任务头2：紧急程度分类（0正常/1关注/2紧急） num_labels=3
    └── 任务头3：情感分值回归（-10~+10）  output=1

三个头共享 BERT 编码层，符合任务书"多任务联合训练、共享编码层"。
"""
import torch
import torch.nn as nn
from transformers import BertModel, BertPreTrainedModel


class MultiTaskBert(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config)
        config.num_labels = 3  # 情感 & 紧急都三分类
        self.sentiment_head = nn.Linear(config.hidden_size, 3)   # 情感倾向
        self.emergency_head = nn.Linear(config.hidden_size, 3)   # 紧急程度
        self.valence_head = nn.Linear(config.hidden_size, 1)     # 情感分值回归
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.post_init()

    def forward(self, input_ids, attention_mask=None, token_type_ids=None,
                labels=None, emergency_labels=None, valence_labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)
        pooled = outputs[1]  # [CLS]
        pooled = self.dropout(pooled)

        sentiment_logits = self.sentiment_head(pooled)
        emergency_logits = self.emergency_head(pooled)
        valence = self.valence_head(pooled).squeeze(-1)

        loss = None
        if labels is not None and emergency_labels is not None and valence_labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_s = loss_fct(sentiment_logits, labels)
            # 紧急分类：类别权重缓解不均衡（正常>关注>紧急）
            emg_weights = torch.tensor([1.0, 2.5, 4.0], device=sentiment_logits.device)
            loss_e = nn.CrossEntropyLoss(weight=emg_weights)(emergency_logits, emergency_labels)
            loss_v = nn.MSELoss()(valence, valence_labels.float())
            # 多任务加权
            loss = loss_s + loss_e + 0.5 * loss_v
            return {"loss": loss, "sentiment_logits": sentiment_logits,
                    "emergency_logits": emergency_logits, "valence": valence}
        return {"sentiment_logits": sentiment_logits,
                "emergency_logits": emergency_logits, "valence": valence}
