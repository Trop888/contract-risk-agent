from agents.document_parser.agent import DocumentParserAgent
from agents.clause_review import ClauseReviewAgent
from agents.rule_checker import RuleCheckAgent
from agents.law_matcher.agent import LawMatcherAgent
from agents.report_generator.agent import ReportGeneratorAgent
from core.model import ContractAnalysisResult, RiskLevel
from core.logger import get_logger

logger = get_logger(__name__)


class ContractAnalysisOrchestrator:
    def __init__(self):
        self.document_parser_agent = DocumentParserAgent()
        self.clause_review_agent = ClauseReviewAgent()
        self.rule_check_agent = RuleCheckAgent()
        self.law_matcher_agent = LawMatcherAgent()
        self.report_generator_agent = ReportGeneratorAgent()

    def parse_files(self, file_paths: list[str]) -> str:
        texts = []
        errors = []
        for path in file_paths:
            logger.info("%s 正在解析 %s ...", self.document_parser_agent.name, path)
            try:
                texts.append(self.document_parser_agent.run(path))
            except Exception as e:
                errors.append(f"{path}: {e}")
                logger.exception("解析失败，已跳过 %s", path)   # 记录完整堆栈，便于排查

        if not texts:
            raise RuntimeError("所有文件解析失败：\n" + "\n".join(errors))
        return "\n\n".join(texts)

    def analyze_text(self, contract_text: str) -> ContractAnalysisResult:
        logger.info("%s 识别风险中...", self.clause_review_agent.name)
        try:
            result = self.clause_review_agent.run(contract_text)
        except Exception as e:
            logger.exception("AI 条款审查失败，降级为仅规则引擎分析")
            result = ContractAnalysisResult(
                is_valid=True,
                summary="AI 条款审查暂时不可用，以下为规则引擎的确定性检查结果。",
                overall_risk=RiskLevel.MEDIUM,
                errors=["AI 智能审查暂时不可用，已自动切换为规则引擎检查，结果可能不完整。"],
            )
        result.contract_text = contract_text
        logger.info("%s 规则预筛中...", self.rule_check_agent.name)
        try:
            rule_items = self.rule_check_agent.run(contract_text)
            if rule_items:
                result.risk_items = rule_items + result.risk_items 
                if any(item.level == RiskLevel.HIGH for item in rule_items):
                    result.overall_risk = RiskLevel.HIGH
        except Exception:
            result.errors.append("规则预筛环节异常，已跳过该环节。")
            logger.exception("规则预筛失败，降级继续")

        if not result.is_valid:
            logger.warning("非有效合同，跳过法规匹配")
            return self.report_generator_agent.run(result)

        logger.info("%s 匹配相关法规中...", self.law_matcher_agent.name)
        try:
            result = self.law_matcher_agent.run(result)
        except Exception:
            result.errors.append("法规匹配服务暂时不可用，部分风险的法律依据可能缺失。")
            logger.exception("法规匹配失败，降级继续")

        logger.info("%s 生成报告中...", self.report_generator_agent.name)
        try:
            result = self.report_generator_agent.run(result)
        except Exception:
            result.errors.append("智能总结生成失败，请参考上方风险清单。")
            result.overall_conclusion = "报告生成异常，请参考上方风险清单，或稍后重试。"
            logger.exception("报告生成失败，降级继续")

        logger.info("合同分析完成")
        return result

    def analyze(self, file_path: str) -> ContractAnalysisResult:
        contract_text = self.parse_files([file_path])
        return self.analyze_text(contract_text)