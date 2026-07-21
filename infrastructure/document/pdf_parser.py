from pypdf import PdfReader
from .base import DocumentParser

class PdfParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        try:
           reader = PdfReader(file_path)
           text = ""
           for page in reader.pages:
               text += page.extract_text() or ""
           return text
        except Exception as e:
           raise ValueError(f"PDF 解析失败，可能已损坏或加密: {e}")
