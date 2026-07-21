"""爬取《民法典》全文网页 → 解析成纯文本 → 存到 data/laws/raw/"""
import os
import requests
from bs4 import BeautifulSoup

# ① 网页地址
url = "https://tjca.miit.gov.cn/zwgk/zcwj/flfg/art/2020/art_20cf1a2e1b854924b5caa744c8045d1f.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# ② 下载网页
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = resp.apparent_encoding
print(f"状态码：{resp.status_code}，长度：{len(resp.text)}")

# ③ 用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(resp.text, "lxml")

# ④ 删掉 script 和 style 标签（这些是代码，不是正文）
for tag in soup(["script", "style"]):
    tag.decompose()

# ⑤ 提取所有文字，用换行分隔
text = soup.get_text(separator="\n")

# ⑥ 存成原始文本
os.makedirs("data/laws/raw/", exist_ok=True)
with open("data/laws/raw/民法典_raw.txt", "w", encoding="utf-8") as f:
    f.write(text)

print(f"已保存纯文本到 data/laws/raw/民法典_raw.txt")
print(f"文本长度：{len(text)} 字符")
print("\n--- 前 500 字预览 ---")
print(text[:500])
print("\n--- 中间部分预览（找找法条）---")
print(text[len(text)//2 : len(text)//2 + 500])