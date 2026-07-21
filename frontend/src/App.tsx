import { useState, useRef } from "react";
import type { ChatMessage, ContractAnalysisResult } from "./types";
import { analyzeFiles } from "./api";
import {
  loadHistory,
  addHistory,
  removeHistory,
  updateHistoryMessages,
  type HistoryRecord,
} from "./history";
import UploadPanel from "./components/UploadPanel";
import ResultView from "./components/ResultView";
import ChatPanel from "./components/ChatPanel";
import HistoryPanel from "./components/HistoryPanel";

function App() {
  const [result, setResult] = useState<ContractAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<HistoryRecord[]>(loadHistory());
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  // 当前选中记录的对话历史
  const currentMessages = history.find((r) => r.id === selectedId)?.messages ?? [];

  async function handleAnalyze(files: File[]) {
    setLoading(true);
    setError("");
    try {
      const data = await analyzeFiles(files);
      setResult(data);
      const title = files.length === 1 ? files[0].name : `${files[0].name} 等 ${files.length} 个文件`;
      const next = addHistory(data, title);
      setHistory(next);
      setSelectedId(next[0].id);
    } catch {
      setError("分析失败，请确认后端已启动（http://localhost:8000）。");
    } finally {
      setLoading(false);
    }
  }

  // 对话有更新 → 存进当前选中的记录
  function handleChatChange(messages: ChatMessage[]) {
    if (!selectedId) return;
    setHistory(updateHistoryMessages(selectedId, messages));
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <h1 className="text-2xl font-bold">📄 合同风险审查助手</h1>
          <p className="mt-1 text-sm text-slate-500">
            上传合同（PDF / Word / TXT / 图片），AI 自动识别风险、匹配法条、生成报告，并支持追问。
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左栏：历史 + 上传 + 结果 */}
        <div className="lg:col-span-2">
          <HistoryPanel
            records={history}
            selectedId={selectedId}
            onSelect={(r) => {
              setResult(r.result);
              setSelectedId(r.id);
              setTimeout(
                () => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
                50
              );
            }}
            onDelete={(id) => setHistory(removeHistory(id))}
          />
          <UploadPanel
            loading={loading}
            onAnalyze={handleAnalyze}
            onReset={() => setResult(null)}
          />
          {error && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}
          <div ref={resultRef}>
            {result && <ResultView result={result} />}
          </div>
        </div>

        {/* 右栏：对话 */}
        <div className="lg:col-span-1">
          <ChatPanel
            key={selectedId ?? "none"}
            result={result}
            initialMessages={currentMessages}
            onMessagesChange={handleChatChange}
          />
        </div>
      </main>
    </div>
  );
}

export default App;