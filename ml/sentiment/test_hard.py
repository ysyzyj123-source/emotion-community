# -*- coding: utf-8 -*-
"""进阶模糊情感测试：结果写入文件便于清晰查看。"""
import requests

BASE = "http://127.0.0.1:5051/predict"

cases = [
    ("绷不住了，真的绷不住了", None),
    ("我人麻了，摆烂吧", None),
    ("今天直接把心态搞崩了，绝了", None),
    ("e得不行，整个人都不好了", None),
    ("破防了家人们", None),
    ("挺好的，我没事，真的没事", None),
    ("哈哈，生活对我真好呢", None),
    ("没事，习惯一个人了", None),
    ("fine，就这样吧", None),
    ("无所谓，反正也没人在意", None),
    ("感觉自己在往下沉，没人拉我", None),
    ("空空的，好像什么都没剩下", None),
    ("窗外的天好灰，跟我一样", None),
    ("胸口闷闷的，说不出来为什么", None),
    ("像掉进一个深不见底的洞", None),
    ("今天也照常吃饭睡觉了", None),
    ("就这样吧，明天还要早起", None),
    ("没什么特别的，老样子", None),
    ("一天又过去了", None),
    ("都挺好的其实", None),
    ("累了，想躺平了，睡很久很久", None),
    ("要是我消失了会有人发现吗", None),
    ("有点想人间蒸发", None),
    ("这房间好安静啊", None),
    ("最近总是做同一个噩梦", None),
    ("终于考完了，但好像也没多开心", None),
    ("拿到offer了，却高兴不起来", None),
    ("大家都夸我，可我一点感觉都没有", None),
]

out = []
for t, _ in cases:
    try:
        d = requests.post(BASE, json={"text": t}, timeout=15).json()
        out.append(f"情感={d['sentiment']} 紧急={d['emergency']} 分值={d['valence']}  |  {t}")
    except Exception as e:
        out.append(f"失败 {e}  |  {t}")

with open("hard_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done", len(out))
