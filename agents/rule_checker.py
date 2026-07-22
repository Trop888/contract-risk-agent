from agents.base import BaseAgent
from core.model import RiskItem, RiskLevel


# 规则库：确定性风险模式（关键词命中即判定，速度快、100% 可复现）
# 与大模型语义审查互补——规则负责"确定的硬伤"，大模型负责"需要理解的风险"
RISK_RULES = [
    {
        "risk_type": "无限责任",
        "keywords": ["无限责任", "无限连带", "承担全部损失", "承担一切", "赔偿无上限", "不设上限"],
        "level": RiskLevel.HIGH,
        "description": "合同中出现无限责任相关表述，一方可能承担超出合理范围的赔偿。",
        "suggestion": "建议将赔偿责任限定在合同总金额的合理比例（如 20%）以内，并明确赔偿范围。",
        "legal_basis": "《民法典》第五百八十五条（违约金应当合理）",
    },
    {
        "risk_type": "单方解除权",
        "keywords": ["单方解除", "单方终止", "有权随时解除", "有权随时终止", "任意解除"],
        "level": RiskLevel.HIGH,
        "description": "合同赋予一方单方解除或终止的权利，另一方权益缺乏保障。",
        "suggestion": "建议约定对等的解除条件与提前通知期，避免权利义务失衡。",
        "legal_basis": "《民法典》第五百六十二条、第五百六十三条（合同的解除）",
    },
    {
        "risk_type": "不合理违约金",
        "keywords": ["双倍赔偿", "三倍赔偿", "全额赔偿", "违约金不低于"],
        "level": RiskLevel.MEDIUM,
        "description": "违约金约定可能过高，超过实际损失过分部分可被认定无效。",
        "suggestion": "建议将违约金约定为可预见损失的合理比例，避免约定过高。",
        "legal_basis": "《民法典》第五百八十五条（约定违约金过分高于损失可请求调整）",
    },
    {
        "risk_type": "自动续约风险",
        "keywords": ["自动续约", "自动续订", "自动展期", "到期自动延长"],
        "level": RiskLevel.MEDIUM,
        "description": "合同包含自动续约条款，若未及时通知可能被动延长履约期限。",
        "suggestion": "建议明确续约需双方书面确认，或约定清晰的到期不续约通知机制。",
        "legal_basis": None,
    },
]

# 必备条款检查：合同中若完全不出现以下任一主题的关键词，视为"条款缺失"风险
REQUIRED_CLAUSES = [
    {
        "risk_type": "缺失争议解决条款",
        "keywords": ["仲裁", "诉讼", "管辖", "争议解决", "争议的解决"],
        "description": "合同未约定争议解决方式，发生纠纷时维权路径不明确。",
        "suggestion": "建议增加争议解决条款，明确仲裁机构或管辖法院。",
    },
    {
        "risk_type": "缺失违约责任条款",
        "keywords": ["违约责任", "违约金", "赔偿"],
        "description": "合同未约定违约责任，一方违约时缺乏追责依据。",
        "suggestion": "建议增加违约责任条款，明确违约情形及赔偿方式。",
    },
]


class RuleCheckAgent(BaseAgent):
    """规则预筛 Agent：用确定性关键词/规则命中高确定性风险，
    作为大模型语义审查前的第一道"硬校验"，速度快、结果可复现，与语义分析互补。"""

    name = "规则预筛agent"

    def run(self, contract_text: str) -> list[RiskItem]:
        items: list[RiskItem] = []

        # 一、命中式风险：出现关键词即判定
        for rule in RISK_RULES:
            hit = next((kw for kw in rule["keywords"] if kw in contract_text), None)
            if hit:
                items.append(RiskItem(
                    risk_type=rule["risk_type"],
                    level=rule["level"],
                    description=rule["description"],
                    clause=self._locate(contract_text, hit),
                    suggestion=rule["suggestion"],
                    legal_basis=rule.get("legal_basis"),
                    source="规则引擎",
                ))

        # 二、缺失式风险：完全不出现相关关键词即判定为条款缺失
        for req in REQUIRED_CLAUSES:
            if not any(kw in contract_text for kw in req["keywords"]):
                items.append(RiskItem(
                    risk_type=req["risk_type"],
                    level=RiskLevel.MEDIUM,
                    description=req["description"],
                    clause=None,
                    suggestion=req["suggestion"],
                    legal_basis=None,
                    source="规则引擎",
                ))

        return items

    @staticmethod
    def _locate(text: str, keyword: str, span: int = 30) -> str | None:
        """截取命中关键词附近的原文片段，方便用户定位。"""
        idx = text.find(keyword)
        if idx == -1:
            return None
        start = max(0, idx - span)
        end = min(len(text), idx + len(keyword) + span)
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        return f"{prefix}{text[start:end]}{suffix}"