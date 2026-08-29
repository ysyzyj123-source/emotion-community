from datasets import load_dataset
import json

ds = load_dataset("XuShihao6715/counseling-cpsdd", split="train")
print("总条数:", len(ds))
print("\n=== 第0条完整字段 ===")
item = ds[0]
for k, v in item.items():
    vstr = str(v)
    print(f"{k}: {vstr[:300]}")
print("\n=== 前5条 messages 结构 ===")
for i in range(min(5, len(ds))):
    it = ds[i]
    print(f"[{i}] topic={it.get('topic')} | client_profile={str(it.get('client_profile'))[:80]}")
    msgs = it.get('messages', [])
    if isinstance(msgs, list):
        for m in msgs[:3]:
            print("   ", str(m)[:120])
