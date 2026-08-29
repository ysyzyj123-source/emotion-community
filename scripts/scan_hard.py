# -*- coding: utf-8 -*-
import json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\毕设\代码\ml\data\sentiment\multitask_train.jsonl'
rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
print(f'总条数: {len(rows)}')

# 难判断场景关键词扫描
hard_scenes = {
    '反讽/讽刺': ['呵呵','呵呵哒','可以啊','真行','真棒','太棒了','真厉害','厉害了','有本事','你行','好家伙','牛逼','秀','绝了','6'],
    '反问/质问': ['难道','凭什么','为什么','怎么可以','谁说的','哪来的','到底为什么'],
    '矛盾/纠结': ['但是','可是','虽然','不过','却又','纠结','左右为难','不知所措','不知道该怎么办'],
    '委屈/被误解': ['委屈','被误解','误会','冤枉','没人理解','不理解我','凭什么对我'],
    '表面坚强/强撑': ['没事','还好','无所谓','习惯了','撑住','还能忍','假装没事','我没事'],
    '口语/网络梗': ['麻了','栓q','emo','破防','绷不住','yyds','笑死','上头','裂开','摆烂','躺平'],
    '求助/求救': ['帮帮我','救救我','怎么办','谁能帮','有没有人','求助','谁在','在线等'],
    '淡化痛苦': ['就那样','还行吧','一般般','凑合','又不是什么大事','算了','别说了'],
    '询问/中性疑问': ['几点','在哪','多少钱','是否','能不能','行不行','什么','怎么样'],
}
print('\n=== 难场景关键词命中 ===')
for scene, kws in hard_scenes.items():
    hits = sum(1 for r in rows if any(k in r['text'] for k in kws))
    print(f'  [{scene}] {hits} 条')

# 情感分布
sent = Counter(r['sentiment'] for r in rows)
emg = Counter(r['emergency'] for r in rows)
print('\n=== 当前分布 ===')
print('情感: 负=%d 正=%d 中性=%d' % (sent.get(0,0),sent.get(1,0),sent.get(2,0)))
print('紧急: 正常=%d 关注=%d 紧急=%d' % (emg.get(0,0),emg.get(1,0),emg.get(2,0)))
