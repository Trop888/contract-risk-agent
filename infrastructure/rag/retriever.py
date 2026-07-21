import os
os.environ["HF_HUB_OFFLINE"] = "1"       
os.environ["TRANSFORMERS_OFFLINE"] = "1"  
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "laws", "chroma_db")

class LawRetriever:

    def __init__(self, db_path: str = DB_PATH):
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-zh-v1.5"
        )
        client = chromadb.PersistentClient(path=db_path)
        self.collection = client.get_collection(
            name="laws",
            embedding_function=embedding_fn,
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        hits = []
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        for doc, meta, dist in zip(docs, metas, dists):
            hits.append({
                "law": meta.get("law", ""),
                "article": meta["article"],
                "chapter": meta["chapter"],
                "text": doc,
                "distance": dist,     
            })
        return hits