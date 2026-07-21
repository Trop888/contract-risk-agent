from .base import DocumentParser

class TxtParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        for encoding in ("utf-8", "gbk", "gb2312"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError("TXT 解析失败，可能已损坏或加密")
