from agents.base import BaseAgent
from infrastructure.document import parse_document

class DocumentParserAgent(BaseAgent):
    name="文档解析agent"
    def run(self, file_path: str) -> str:
        return parse_document(file_path)