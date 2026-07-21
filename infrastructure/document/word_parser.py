import docx
from docx.text.paragraph import Paragraph
from docx.table import Table
from .base import DocumentParser

class WordParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        try:
            doc = docx.Document(file_path)
            parts = []

            body = doc.element.body
            for child in body.iterchildren():
                if child.tag.endswith("}p"):          
                    para = Paragraph(child, doc)
                    if para.text.strip():
                        parts.append(para.text)
                elif child.tag.endswith("}tbl"):      
                    table = Table(child, doc)
                    for row in table.rows:
                        cells = [cell.text.strip() for cell in row.cells]
                        row_text = " | ".join(cells)
                        if row_text.strip(" |"):
                            parts.append(row_text)

            return "\n".join(parts)
        except Exception as e:
            raise ValueError(f"Word 解析失败（可能已损坏）：{e}")