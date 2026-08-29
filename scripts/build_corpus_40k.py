# -*- coding: utf-8 -*-
"""40000条均衡语料生成：各等级补差到配额。"""
import json, os, random
from collections import Counter

random.seed(42)
BASE = r'D:\毕设\代码\ml\data\sentiment'
OUT = os.path.join(BASE, 'multitask_train.jsonl')
TARGET = 40000

# 目标配额：正/负/中性 各约 1/3；紧急要均衡可控
SENT_TARGET = {0: 13300, 1: 13400, 2: 13300}

# ---- 各类语料 ----
POS_LOVE = ["我爱你","我很爱你","我好喜欢你","我喜欢你很久了","我们在一起好幸福","和他在一起每天都很甜","好想你","我好想念你","男朋友出差了好想他","和你在一起的每一天都好开心","我喜欢看你笑","你对我真好，好爱你","她答应做我女朋友了，太幸福了","我们互相喜欢，在一起了"]
POS_WARM = ["被朋友关心真的好暖","室友给我带了早餐，好感动","家人打电话来很安心","谢谢你一直陪着我","朋友记得我生日，好幸福","老师鼓励我，很暖心","妈妈做的饭最好吃，好温暖","收到大家的祝福，特别感动","闺蜜陪我度过难关，感恩有你","被喜欢的人关心，心里好暖"]
POS_FUN = ["今天打游戏赢了，超开心","追星成功好激动","看剧上头了停不下来","和室友看综艺笑死了","吃到了超好吃的火锅，太满足了","去游乐园玩了一天，太快乐了","刷到了好笑的视频，笑不活了","和朋友唱了一下午歌，超放松","买了喜欢的手办，好开心","周末去野餐，心情好好"]
POS_ACH = ["考研上岸了，太高兴了","拿到奖学金，特别激动","比赛获奖了，好骄傲","考试全过了，一身轻松","实习转正了，前途光明","论文通过了，太开心了","拿到了心仪的offer，高兴坏了","终于考过六级了，好有成就感","攒钱买到了心仪的东西，开心","学会了新技能，成就感满满"]
POS_NAUGHTY = ["讨厌，你真好","你好坏哦，但我喜欢","傻样，我心疼你","别闹了，我好喜欢你","你真可爱，我好喜欢","坏蛋，抱抱"]
POS_EXTRA = ["考上研究生了，超开心","拿到驾照了，好有成就感","第一次做菜成功了，好棒","被老师表扬了，心里美滋滋","吃到妈妈做的排骨，好幸福","去看演唱会了，超激动"]

NEUT = ["我今天去图书馆自习","中午吃了食堂的饭","准备睡觉了","刚下课回宿舍","这个周末打算去爬山","下午有两节课","去超市买了点东西","刚洗完澡","今天天气不错，出去走了走","晚上看了会儿书","定了闹钟准备早起","收拾了一下宿舍","去食堂打饭","复习了一章内容","开了个小会","陪朋友去取快递","明天有早八","看了会儿手机","整理了下笔记","今天课表比较满","刚买了一杯奶茶","在操场走了几圈","去快递站拿包裹","老师布置了作业","今天没课，睡了个懒觉","去操场跑了步","食堂新出了个菜","刚打完电话","等公交去市区","看了眼新开的店","回家睡了个午觉","今天吃了螺蛳粉"]

NEG_MILD = ["作业太多了，写不完","上早八真的好累","食堂饭又涨价了","舍友打呼噜睡不着","今天状态好差，不在状态","电脑又卡了，好烦","外卖送超时了，饿死了","好多课都不想上","排队排了好久","天气好热，受不了","emo了，好难过","好想摆烂，什么都不想干"]
NEG_MID = ["期末压力好大，很焦虑","最近失眠，精神状态差","和室友吵架了，很难受","找工作一直没回音，好焦虑","喜欢的人有对象了，好难过","考研复习到崩溃，坚持不住了","被导师批评了，很沮丧","和好朋友冷战了，心里堵得慌","异地恋好难，好想她","一个人好孤独，没人理解我","被喜欢的人拒绝了，好失落","压力大到快崩溃了"]
NEG_HIGH = ["我真的撑不下去了，想死","活着好累，我想轻生","好想跳楼，解脱算了","不想活了，想消失","我撑不住了，想结束这一切"]

def add_random(rows, pool, sentiment, emergency, valence_range, count):
    for _ in range(count):
        rows.append({'text': random.choice(pool), 'sentiment': sentiment, 'emergency': emergency,
                     'valence': round(random.uniform(*valence_range), 1)})

def build():
    # 现有负向语料（作为负向一部分）
    existing_neg = []
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r['sentiment'] == 0:
                    existing_neg.append(r)
    # 现有负向按紧急度分层
    neg_c = Counter(r['emergency'] for r in existing_neg)
    print(f"现有负向: {len(existing_neg)} (正常{neg_c.get(0,0)} 关注{neg_c.get(1,0)} 紧急{neg_c.get(2,0)})")

    rows = []
    # 负向配额分层：正常/关注/紧急
    neg_want = SENT_TARGET[0]  # 13300
    n_normal = neg_want // 2            # 轻度/一般负向 -> 正常
    n_concern = int(neg_want * 0.35)    # 中度负向 -> 关注
    n_urgent = neg_want - n_normal - n_concern  # 高危 -> 紧急 (~2000)

    # 从现有负向中按紧急度分层取，补足
    from collections import defaultdict
    by_emg = defaultdict(list)
    for r in existing_neg:
        by_emg[r['emergency']].append(r)

    take_normal = by_emg[0][:n_normal]
    take_concern = by_emg[1][:n_concern]
    take_urgent = by_emg[2][:n_urgent]
    rows += take_normal + take_concern + take_urgent

    # 若某项不足，用生成补
    cur_normal = len([r for r in rows if r['emergency']==0 and r['sentiment']==0])
    if cur_normal < n_normal:
        add_random(rows, NEG_MILD, 0, 0, (-4.5,-1.0), n_normal - cur_normal)
    cur_concern = len([r for r in rows if r['emergency']==1])
    if cur_concern < n_concern:
        add_random(rows, NEG_MID, 0, 1, (-8.0,-5.0), n_concern - cur_concern)
    cur_urgent = len([r for r in rows if r['emergency']==2])
    if cur_urgent < n_urgent:
        add_random(rows, NEG_HIGH, 0, 2, (-9.5,-10.0), n_urgent - cur_urgent)

    # 3) 正向配额
    pos_want = SENT_TARGET[1]
    pos_cur = len([r for r in rows if r['sentiment']==1])
    need = pos_want - pos_cur
    pools = [POS_LOVE, POS_WARM, POS_FUN, POS_ACH, POS_NAUGHTY, POS_EXTRA]
    per = need // len(pools)
    for pool in pools:
        add_random(rows, pool, 1, 0, (6.0, 9.5), per)
    # 剩余补
    rem = pos_want - len([r for r in rows if r['sentiment']==1])
    add_random(rows, POS_LOVE, 1, 0, (6.0, 9.5), max(rem,0))

    # 4) 中性配额
    neu_want = SENT_TARGET[2]
    neu_cur = len([r for r in rows if r['sentiment']==2])
    need = neu_want - neu_cur
    add_random(rows, NEUT, 2, 0, (-1.0, 1.0), need)

    random.shuffle(rows)
    # 精确到40000
    if len(rows) > TARGET:
        # 随机移除多余（尽量不破坏均衡）
        rows = random.sample(rows, TARGET)
    elif len(rows) < TARGET:
        while len(rows) < TARGET:
            rows.append(dict(random.choice(rows)))
    random.shuffle(rows)

    with open(OUT, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    sent = Counter(r['sentiment'] for r in rows)
    emg = Counter(r['emergency'] for r in rows)
    print(f"\n最终 {len(rows)} 条")
    print(f"  情感: 负={sent.get(0,0)} 正={sent.get(1,0)} 中性={sent.get(2,0)}")
    print(f"  紧急: 正常={emg.get(0,0)} 关注={emg.get(1,0)} 紧急={emg.get(2,0)}")

if __name__ == '__main__':
    build()
