"""对单份合同做临时（内存）向量检索：合同过长时，只取与问题相关的条款"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ContractRetriever:
    def __init__(self):
        # 复用和法规库同一个中文向量模型
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-zh-v1.5"
        )
        # 文本切分器：每块约500字，块间重叠80字（避免把一句话从中间切断）
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n", "\n", "。", "；", " ", ""],
        )

    def retrieve(self, contract_text: str, query: str, top_k: int = 5) -> str:
        # ① 把合同切成小块
        chunks = self.splitter.split_text(contract_text)
        if not chunks:
            return contract_text

        # ② 建一个"用完即弃"的内存向量库，把块存进去
        client = chromadb.EphemeralClient()
        collection = client.create_collection(
            name="contract_tmp",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        ids = [f"chunk-{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)

        # ③ 检索与问题最相关的若干块，拼成上下文返回
        n = min(top_k, len(chunks))
        results = collection.query(query_texts=[query], n_results=n)
        return "\n...\n".join(results["documents"][0])