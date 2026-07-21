"""对话问答 Agent：基于已分析的合同，回答用户的追问"""
from agents.base import BaseAgent
from infrastructure.llm import get_llm_service
from infrastructure.rag.retriever import LawRetriever
from infrastructure.rag.contract_retriever import ContractRetriever

QA_SYSTEM_PROMPT = """你是一位专业的合同法律顾问助手。用户会就下面这份合同向你提问，请遵守：
1. 优先依据【合同内容】和【相关法律条文】回答，做到有理有据；
2. 回答务必简洁：直接给结论，控制在 3 句话、150 字以内；不要罗列大段法条原文，不要背景铺垫和客套；
3. 面向不懂法律的普通用户，用大白话说清楚；如需引用法条，只点名称+核心意思，不抄全文；
4. 若合同和法条中都找不到依据，就如实说"合同中未提及"或"建议咨询专业律师"，切勿编造条款或法条。
【合同内容】
{contract_text}

【相关法律条文】
{law_reference}"""

LONG_CONTRACT_CHARS = 4000 

class ContractQAAgent(BaseAgent):
    name = "问答Agent"

    def __init__(self):
        self.llm = get_llm_service()
        self.retriever = LawRetriever()
        self.contract_retriever = ContractRetriever()

    def run(self, question: str, contract_text: str, history: list[dict]) -> str:
        # 针对本次问题检索相关法条
        hits = self.retriever.retrieve(question, top_k=3)
        law_reference = "\n\n".join(h["text"] for h in hits) or "（无相关法条）"

        # 合同上下文：短合同用全文；长合同只检索与问题相关的条款，避免超出模型上下文
        if len(contract_text) > LONG_CONTRACT_CHARS:
            contract_context = self.contract_retriever.retrieve(contract_text, question, top_k=5)
        else:
            contract_context = contract_text

        # 组装消息：系统提示(含合同+法条) + 历史对话 + 本次提问
        system_prompt = QA_SYSTEM_PROMPT.format(
            contract_text=contract_context,
            law_reference=law_reference,
        )
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)                                   # 历史对话
        messages.append({"role": "user", "content": question})     # 本次提问

        return self.llm.chat(messages, temperature=0.3)