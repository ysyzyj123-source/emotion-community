from datasets import load_dataset_builder
names = [
    'XuShihao6715/counseling-cpsdd',
    'chillies/student-mental-health-chat-data-v1',
]
for n in names:
    try:
        b = load_dataset_builder(n)
        splits = b.info.splits or {}
        print(n)
        total = 0
        for split, info in splits.items():
            n_ex = info.num_examples
            total += n_ex
            print('  split', split, '=', n_ex)
        print('  总条数:', total)
        feat = list((b.info.features or {}).keys())
        print('  字段:', feat)
        print()
    except Exception as e:
        print(n, '获取失败', type(e).__name__, str(e)[:120])
        print()
