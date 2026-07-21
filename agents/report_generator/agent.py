from agents.base import BaseAgent
from infrastructure.llm import get_llm_service
from core.model import ContractAnalysisResult, RiskItem, RiskLevel

RISK_ORDER = {RiskLevel.HIGH: 0,RiskLevel.MEDIUM: 1,RiskLevel.LOW: 2}

REPORT_SYSTEM_PROMPT = """你是一位资深的合同法律顾问。请基于给定的合同风险清单，用2-3句话总结，
1.风险概况（有几项高风险，有几项中风险，有几项低风险）
2.给出明确的签署结论，从「可以签署」「修改后签署」「不建议签署」中选最贴切的一个，用自然通顺的话陈述，避免"建议不建议"之类的重复措辞
语言简洁专业、面向普通用户（企业主或个人），让对方一眼就知道该怎么做。直接输出结论文字，不要用JSON，不要加标题。"""

class ReportGeneratorAgent(BaseAgent):
    name = "报告生成agent"

    def __init__(self):
        self.llm = get_llm_service()

    def run(self,result:ContractAnalysisResult) -> ContractAnalysisResult:
        result.risk_items.sort(key=lambda x:RISK_ORDER[x.level])
        if not result.is_valid:
            result.overall_conclusion = "该文本无法作为有效合同进行审查，请检查文本内容。"
            return result
        if not result.risk_items:
            result.overall_conclusion = "合同未发现明显风险，可在确认细节后签署。"
            return result
        
        risk_brief="\n".join(f"-[{item.level}] {item.risk_type}: {item.description}" for item in result.risk_items)
        messages=[
            {"role":"system","content":REPORT_SYSTEM_PROMPT},
            {"role":"user","content":f"合同摘要：{result.summary}\n\n风险清单：\n{risk_brief}"},
        ]
        result.overall_conclusion=self.llm.chat(messages,temperature=0.2)
        return result