from datasets import load_dataset
from collections import Counter

ds = load_dataset("XuShihao6715/counseling-cpsdd", split="train")
print("总条数:", len(ds))

sevs = Counter(); probs = Counter(); groups = Counter()
for i in range(min(3000, len(ds))):
    p = ds[i].get("client_profile") or {}
    sevs[p.get("start_severity")] += 1
    probs[p.get("psychological_problem")] += 1
    groups[p.get("group")] += 1

print("=== 严重度分布 ===")
for k, v in sorted(sevs.items(), key=lambda x: str(x[0])):
    print(f"  severity={k}: {v}")
print("=== 心理问题类型(前15) ===")
for k, v in probs.most_common(15):
    print(f"  {k}: {v}")
print("=== 群体类型(前10) ===")
for k, v in groups.most_common(10):
    print(f"  {k}: {v}")
