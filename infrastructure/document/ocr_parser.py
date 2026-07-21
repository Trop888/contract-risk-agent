from .base import DocumentParser

class OcrParser(DocumentParser):
    def __init__(self):
        self._ocr = None  # 懒加载：用到时才初始化，避免启动就占 2GB 内存

    @property
    def ocr(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(enable_mkldnn=False, lang='ch')
        return self._ocr

    def parse(self, file_path: str) -> str:
        result = self.ocr.predict(file_path)

        texts=[]
        for res in result:
            rec_texts = res["rec_texts"]                   # ← 直接取，不用 res["res"]
            rec_scores = res["rec_scores"]
            for text, score in zip(rec_texts, rec_scores):
                if score > 0.3:  # 只保留置信度大于0.3的文本
                    texts.append(text)

        return '\n'.join(texts)
