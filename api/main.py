import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from agents.report_generator.word_report import build_word_report
from pydantic import BaseModel

from core.orchestrator import ContractAnalysisOrchestrator
from core.model import ContractAnalysisResult
from agents.qa_agent import ContractQAAgent

app = FastAPI(title="合同风险审查 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = ContractAnalysisOrchestrator()
qa_agent = ContractQAAgent()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=ContractAnalysisResult)
async def analyze(files: list[UploadFile] = File(...)):
    """上传一个或多个文件（视为同一份合同）→ 返回完整分析结果"""
    tmp_paths = []
    try:
        for f in files:
            suffix = os.path.splitext(f.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await f.read())
                tmp_paths.append(tmp.name)
        contract_text = orchestrator.parse_files(tmp_paths)
        return orchestrator.analyze_text(contract_text)
    finally:
        for p in tmp_paths:
            os.remove(p)


class ChatRequest(BaseModel):
    question: str
    contract_text: str
    history: list[dict] = []


@app.post("/chat")
def chat(req: ChatRequest):
    answer = qa_agent.run(
        question=req.question,
        contract_text=req.contract_text,
        history=req.history,
    )
    return {"answer": answer}

@app.post("/report")
def report(result: ContractAnalysisResult):
    data = build_word_report(result)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=contract_report.docx"},
    )