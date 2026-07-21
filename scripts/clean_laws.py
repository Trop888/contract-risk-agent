import re
import json
import os

LAW_NAME = "民法典"

RAW_PATH = f"data/laws/raw/{LAW_NAME}_raw.txt"
OUT_PATH = f"data/laws/cleaned/{LAW_NAME}_articles.json"

with open(RAW_PATH, "r", encoding="utf-8") as f:
    raw = f.read()

lines = [line.strip() for line in raw.split("\n")]
lines = [line for line in lines if line]

re_article = re.compile(r"^第[一二三四五六七八九十百千零两]+条")
re_heading = re.compile(r"^第[一二三四五六七八九十百千零两]+(编|章|节|分编)")

def normalize(text: str) -> str:
    text = re.sub(r"[\u2002\u3000\xa0\s]+", " ", text)
    return text.strip()

articles = []
current = None
current_chapter = ""

for line in lines:
    if re_heading.match(line):
        current_chapter = normalize(line)
        continue
    m = re_article.match(line)
    if m:
        if current:
            articles.append(current)
        rest = line[m.end():].strip()
        current = {
            "law": f"《{LAW_NAME}》",      
            "chapter": current_chapter,
            "article": m.group(),
            "content": rest,
        }
    else:
        if current is not None:
            current["content"] += line

if current:
    articles.append(current)

print(f"✅ [{LAW_NAME}] 共提取 {len(articles)} 条法条")
empty = [a["article"] for a in articles if not a["content"]]
print(f"⚠️ 空内容的条数：{len(empty)}")
if empty:
    print("   空内容示例：", empty[:5])

os.makedirs("data/laws/cleaned", exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f"✅ 已保存到 {OUT_PATH}")

print("\n--- 前 3 条预览 ---")
for a in articles[:3]:
    print(a)