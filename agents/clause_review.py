import json
from infrastructure.llm import get_llm_service
from core.model import ContractAnalysisResult
from agents.base import BaseAgent
from .prompts import CLAUSE_REVIEW_SYSTEM_PROMPT

class ClauseReviewAgent(BaseAgent):
    name = "条款审查agent"
    def __init__(self):
        self.llm=get_llm_service()

    def run(self,contract_text:str) -> ContractAnalysisResult:
        messages=[
            {"role":"system","content":CLAUSE_REVIEW_SYSTEM_PROMPT},
            {"role":"user","content":contract_text}
        ]
        response=self.llm.chat(messages,temperature=0.2,response_format={"type":"json_object"})
        data=json.loads(response)
        return ContractAnalysisResult(**data)