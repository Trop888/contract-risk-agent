from infrastructure.rag.retriever import LawRetriever

retriever = LawRetriever()

# 试几个查询（故意用“大白话”，看它能不能匹配到法条）
queries = [
    "押金到期不退还怎么办",
    "租金太高违约金过高",
    "房东提前收回房子",
]

for q in queries:
    print(f"\n{'='*50}")
    print(f"🔍 查询：{q}")
    print('='*50)
    hits = retriever.retrieve(q, top_k=3)
    for i, h in enumerate(hits, 1):
        print(f"\n[{i}] {h['chapter']} {h['article']}（距离 {h['distance']:.3f}）")
        print(f"    {h['text'][:60]}...")