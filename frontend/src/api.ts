import axios from "axios";
import type { ContractAnalysisResult, ChatMessage } from "./types";

const API_BASE = "http://localhost:8000";
const client = axios.create({ baseURL: API_BASE });

// ① 上传文件 → 分析
export async function analyzeFiles(files: File[]): Promise<ContractAnalysisResult> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const resp = await client.post<ContractAnalysisResult>("/analyze", form, {
    timeout: 300000, // 分析较慢，给 5 分钟
  });
  return resp.data;
}

// ② 追问
export async function chat(
  question: string,
  contractText: string,
  history: ChatMessage[]
): Promise<string> {
  const resp = await client.post<{ answer: string }>(
    "/chat",
    { question, contract_text: contractText, history },
    { timeout: 180000 }
  );
  return resp.data.answer;
}

// ③ 下载 Word 报告
export async function downloadReport(result: ContractAnalysisResult): Promise<void> {
  const resp = await client.post("/report", result, { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([resp.data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = "contract_report.docx";
  a.click();
  window.URL.revokeObjectURL(url);
}