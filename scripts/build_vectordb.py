import json
import chromadb
from chromadb.utils import embedding_functions
import os
os.environ["HF_HUB_OFFLINE"] = "1"        # 强制离线：只用本地缓存
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "laws", "chroma_db")
CLEANED_DIR = os.path.join(PROJECT_ROOT, "data", "laws", "cleaned")

LAW_FILES = [
    "民法典_articles.json",
    "劳动合同法_articles.json",
]

print("📁 向量库将建在：", DB_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)

client = chromadb.PersistentClient(path=DB_PATH)
try:
    client.delete_collection("laws")
    print("🧹 已删除旧的 laws 集合，准备全量重建")
except Exception:
    pass
collection = client.create_collection(
    name="laws",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"},
)

documents, metadatas, ids = [], [], []

for law_file in LAW_FILES:
    path = os.path.join(CLEANED_DIR, law_file)
    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"加载 {law_file}：{len(articles)} 条")

    for i, a in enumerate(articles):
        law = a.get("law", "")
        text = f"{law} {a['article']} {a['content']}"
        documents.append(text)
        metadatas.append({"law": law, "article": a["article"], "chapter": a["chapter"]})
        ids.append(f"{law_file.replace('_articles.json', '')}-{i}")

print(f"正在向量化并存入 ChromaDB，共 {len(documents)} 条，请耐心等...")
collection.add(documents=documents, metadatas=metadatas, ids=ids)

print(f"✅ 建库完成！共存入 {collection.count()} 条法规向量")
print("向量库保存在：", DB_PATH)