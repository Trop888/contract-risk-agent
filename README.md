# 合同风险审查 AI Agent（Contract Risk Review Agent）

> 一款基于**多 Agent 编排**与 **RAG（检索增强生成）** 的智能合同审查系统：上传合同即可自动识别风险条款、匹配法律依据、生成 Word 审查报告，并支持基于合同内容的多轮追问。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688)
![React](https://img.shields.io/badge/React-TypeScript-61dafb)
![RAG](https://img.shields.io/badge/RAG-ChromaDB-orange)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)

---

## 📸 效果展示

### RAG 法规匹配与结构化报告
每项风险附带原文条款定位、修改建议，以及基于 RAG 检索的《民法典》等法律依据。
![完整报告](images/3.png)




### 规则 + 大模型双引擎风险识别
同一份合同中，规则引擎（⚡ 确定性命中）与大模型（🤖 语义分析）并行工作、互为补充。
![双引擎](images/1.png)




### 故障隔离与分级降级
故意使大模型不可用（API Key 失效）时，系统不崩溃：自动降级为规则引擎分析，
如实向用户提示降级信息，核心可用性不受单点故障影响。
![故障隔离](images/2.png)




### 交互式追问
分析完成后可就合同细节多轮追问，回答能引用具体合同条款与法条。
![交互式追问](images/4.png)




## ✨ 功能特性

- 📄 **多格式解析**：支持 PDF / Word / TXT / 图片（OCR），多文件视为同一份合同合并分析
- ⚡ **双引擎风险识别**：规则引擎（确定性关键词命中 + 缺失条款检测，秒级、可复现）与大模型（语义分析）互补，风险项标注来源（⚡规则引擎 / 🤖AI审查），兼顾"不漏硬伤"与"深层理解"
- 🔍 **LLM 结构化输出**：逐条识别风险类型、等级（高/中/低）、法律依据与修改建议
- ⚖️ **法规匹配（RAG）**：从《民法典》《劳动合同法》向量库中检索相关法条，为每条风险提供法律依据
- 📊 **结构化报告**：一键生成并下载 Word 审查报告
- 💬 **智能追问**：针对已分析合同多轮问答，RAG 增强、有理有据
- 🕓 **历史记录**：前端本地持久化（localStorage），可回看历次分析与对话

---

## 🏗️ 系统架构

采用**编排器（Orchestrator）+ 多 Agent**设计，各 Agent 职责单一、可插拔、故障隔离：

```mermaid
flowchart LR
    U([用户上传合同]) --> P[📄 文档解析 Agent]
    P --> K[⚡ 规则预筛 Agent<br/>确定性规则命中]
    P --> R[🔍 条款审查 Agent<br/>LLM 语义分析]
    K --> L
    R -->|有效合同| L[⚖️ 法规匹配 Agent<br/>RAG 检索法条]
    R -->|非合同/无效| Rep
    L --> Rep[📊 报告生成 Agent]
    Rep --> Res([结构化结果 + Word 报告])
    Res -.多轮追问.-> Q[💬 问答 Agent<br/>RAG 增强]
```

| Agent | 职责 |
|-------|------|
| **文档解析 Agent** | 统一解析 PDF / Word / TXT / 图片，输出纯文本 |
| **规则预筛 Agent** | 用确定性规则库命中"无限责任/单方解除"等硬伤 + 检测缺失条款，秒级、可复现 |
| **条款审查 Agent** | 调用 LLM 结构化输出，识别需语义理解的风险条款 |
| **法规匹配 Agent** | 用 RAG 检索最相关法条，补充法律依据 |
| **报告生成 Agent** | 汇总总体结论、生成 Word 报告 |
| **问答 Agent** | 基于合同 + 检索法条，回答用户追问 |

---

## 🛠️ 技术栈

| 层 | 技术 |
|----|------|
| **后端** | Python · FastAPI · Pydantic · Uvicorn |
| **大模型** | DeepSeek（OpenAI 兼容接口，模型层可插拔） |
| **RAG** | ChromaDB（向量数据库） · sentence-transformers（`BAAI/bge-small-zh-v1.5` 中文向量模型） |
| **文档处理** | PyMuPDF · python-docx · PaddleOCR |
| **前端** | React · TypeScript · Vite · Tailwind CSS · axios |
| **测试** | pytest（规则引擎单元测试，覆盖命中/缺失/防误报/可复现） |
| **知识库** | 《中华人民共和国民法典》《劳动合同法》（按条切分、向量化） |

---

## 📁 项目结构

```
contract-risk-agent/
├── agents/                 # 各功能 Agent（解析/规则预筛/审查/法规匹配/报告/问答）
├── core/                   # 编排器 orchestrator + 数据模型 model
├── infrastructure/         # 基础设施：LLM 服务、RAG 检索、文档解析
│   ├── llm/                # 大模型服务（可插拔）
│   ├── rag/                # 向量检索
│   └── document/           # 多格式文档解析
├── api/                    # FastAPI 接口层（main.py）
├── frontend/               # React + TS 前端
├── scripts/                # 建库/清洗/爬取脚本
├── tests/                  # pytest 单元测试（规则引擎）
├── data/laws/              # 法规原文、清洗结果、向量库
└── requirements.txt
```

---

## 🚀 快速开始

### 1. 后端

```bash
# 克隆项目
git clone https://github.com/Trop888/contract-risk-agent.git
cd contract-risk-agent

# 创建虚拟环境并安装依赖
python -m venv venv
venv\Scripts\activate          # Windows；macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

在根目录新建 `.env` 文件，填入你的 API 密钥：

```env
DEEPSEEK_API_KEY=你的_deepseek_密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

> ⚠️ 向量库不随仓库分发，首次使用请先构建：`python scripts/build_vectordb.py`（会读取 `data/laws/cleaned/` 下的法规并写入 ChromaDB）

启动后端：

```bash
python -m uvicorn api.main:app --reload --port 8000
```

访问 http://localhost:8000/health 返回 `{"status":"ok"}` 即成功。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173 即可使用。

### 3. 运行测试

```bash
python -m pytest tests/ -v
```

覆盖规则引擎的命中、缺失条款、防误报与结果可复现等场景。

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/analyze` | 上传合同文件，返回结构化分析结果 |
| POST | `/chat` | 基于合同内容的多轮追问 |
| POST | `/report` | 生成并下载 Word 审查报告 |

---

## 💡 设计亮点

- **规则 + 大模型双引擎**：确定性规则引擎负责"不漏关键词硬伤"（秒级、可复现），大模型负责"深层语义理解"，二者互补并在结果中标注来源，兼顾召回率与准确率
- **多 Agent 职责分离**：解析、规则预筛、审查、法规匹配、报告、问答各司其职，便于扩展与维护
- **模型/向量库可插拔**：LLM 服务抽象为接口，更换模型无需改业务代码
- **RAG 落地**：法规按条切分 + 向量检索，让 AI 的风险判断"有法可依"、减少幻觉
- **前后端分离**：FastAPI 提供 RESTful 接口，React 独立前端，通过 CORS 通信
- **故障隔离与分级降级**：多 Agent 流水线中，法规匹配、报告生成等增强环节用异常隔离包裹，单个 Agent 失败不会中断整体分析——核心风险清单照常返回，仅缺失的部分通过 `errors` 字段贯穿到前端明确提示，避免"沉默降级"，兼顾高可用与结果可信度
- **单元测试保障**：规则引擎为纯确定性逻辑，用 pytest 覆盖命中/缺失/防误报/可复现，改动规则库时能立即发现回归

---

## 📄 声明

本项目为个人学习与技术演示用途，分析结果仅供参考，不构成法律意见。