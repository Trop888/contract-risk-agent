from agents.base import BaseAgent
from infrastructure.rag.retriever import LawRetriever
from core.model import ContractAnalysisResult

DISTANCE_THRESHOLD = 0.5
class LawMatcherAgent(BaseAgent):
    name="法规匹配agent"
    def __init__(self):
        self.retriever=LawRetriever()
    def run(self,result:ContractAnalysisResult) -> ContractAnalysisResult:
        for item in result.risk_items:
            query=f"{item.risk_type} {item.description}"
            hits=self.retriever.retrieve(query,top_k=3)
            matched=[h for h in hits if h["distance"]<DISTANCE_THRESHOLD]
            if matched:
                item.legal_basis="；".join(h['text'] for h in matched)
        return result