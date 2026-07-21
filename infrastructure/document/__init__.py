import os
from .base import DocumentParser
from .pdf_parser import PdfParser
from .word_parser import WordParser
from .txt_parser import TxtParser

def get_parser(file_path: str) -> DocumentParser:
    ext=os.path.splitext(file_path)[1].lower()
    if ext==".pdf":
        return PdfParser()
    elif ext==".doc" or ext==".docx":
        return WordParser()
    elif ext==".txt":
        return TxtParser()
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        from .ocr_parser import OcrParser
        return OcrParser()
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

def parse_document(file_path: str) -> str:
    parser = get_parser(file_path)
    text = parser.parse(file_path)
    if len(text.strip())<10:
        raise ValueError("未提取到有效文字，可能是扫描件、空文档或图片型PDF，请检查文件内容。")
    return text
