from agents.document_parser.agent import DocumentParserAgent
from agents.clause_review import ClauseReviewAgent
from agents.law_matcher.agent import LawMatcherAgent
from agents.report_generator.agent import ReportGeneratorAgent
from core.model import ContractAnalysisResult


class ContractAnalysisOrchestrator:
    def __init__(self):
        self.document_parser_agent = DocumentParserAgent()
        self.clause_review_agent = ClauseReviewAgent()
        self.law_matcher_agent = LawMatcherAgent()
        self.report_generator_agent = ReportGeneratorAgent()

    def parse_files(self, file_paths: list[str]) -> str:
        """解析一个或多个文件，拼接成一整段合同文本"""
        texts = []
        errors = []
        for path in file_paths:
            print(f"▶ {self.document_parser_agent.name} 正在解析 {path} ...")
            try:
                texts.append(self.document_parser_agent.run(path))
            except Exception as e:
                errors.append(f"{path}: {e}")
                print(f"⚠ 解析失败，已跳过 {path}：{e}")

        if not texts:
            raise RuntimeError("所有文件解析失败：\n" + "\n".join(errors))
        return "\n\n".join(texts)

    def analyze_text(self, contract_text: str) -> ContractAnalysisResult:
        """基于已解析的合同文本，跑完 审查→匹配→报告"""
        print(f"▶ {self.clause_review_agent.name} 识别风险中...")
        result = self.clause_review_agent.run(contract_text)
        result.contract_text = contract_text

        if not result.is_valid:
            print("⚠ 非有效合同，跳过法规匹配")
            return self.report_generator_agent.run(result)

        print(f"▶ {self.law_matcher_agent.name} 匹配相关法规中...")
        try:
            result = self.law_matcher_agent.run(result)
        except Exception as e:
            result.errors.append(f"法规匹配失败：{e}")
            print(f"⚠ 法规匹配失败，降级继续：{e}")

        print(f"▶ {self.report_generator_agent.name} 生成报告中...")
        try:
            result = self.report_generator_agent.run(result)
        except Exception as e:
            result.errors.append(f"报告生成失败：{e}")
            result.overall_conclusion = "报告生成异常，请参考上方风险清单，或稍后重试。"   # 兜底，避免前端空白
            print(f"⚠ 报告生成失败，降级继续：{e}")
        print("✅ 合同分析完成")
        return result

    def analyze(self, file_path: str) -> ContractAnalysisResult:
        """单文件分析（保留，向后兼容）"""
        contract_text = self.parse_files([file_path])
        return self.analyze_text(contract_text)