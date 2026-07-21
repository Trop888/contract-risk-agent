import { useState, useEffect, useRef } from "react";
import type { ChatMessage, ContractAnalysisResult } from "../types";
import { chat } from "../api";

interface Props {
  result: ContractAnalysisResult | null;
  initialMessages: ChatMessage[];
  onMessagesChange: (messages: ChatMessage[]) => void;
}

export default function ChatPanel({ result, initialMessages, onMessagesChange }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const hasResult = !!result && result.is_valid;

  // 有新消息 → 自动滚到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend() {
    const question = input.trim();
    if (!question || !hasResult || loading) return;
    setInput("");
    const next = [...messages, { role: "user", content: question } as ChatMessage];
    setMessages(next);
    onMessagesChange(next); // 存一次（用户提问）
    setLoading(true);
    try {
      const answer = await chat(question, result!.contract_text ?? "", messages);
      const final = [...next, { role: "assistant", content: answer } as ChatMessage];
      setMessages(final);
      onMessagesChange(final); // 存一次（AI 回答）
    } catch {
      const final = [...next, { role: "assistant", content: "⚠️ 回答失败，请重试。" } as ChatMessage];
      setMessages(final);
      onMessagesChange(final);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="sticky top-6 flex h-[calc(100vh-8rem)] flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 font-semibold text-slate-800">💬 追问合同细节</div>

      {/* 历史区：独立滚动 */}
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {!hasResult ? (
          <p className="text-sm text-slate-400">请先在左侧上传并分析合同，然后在这里追问 👈</p>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
              <div
                className={
                  "inline-block max-w-[85%] rounded-2xl px-3 py-2 text-sm " +
                  (m.role === "user" ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-800")
                }
              >
                {m.content}
              </div>
            </div>
          ))
        )}
        {loading && <p className="text-sm text-slate-400">思考中...</p>}
        <div ref={bottomRef} />
      </div>

      {/* 输入区 */}
      <div className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={!hasResult || loading}
          placeholder="例如：违约金多少算合理？"
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500 disabled:bg-slate-50"
        />
        <button
          onClick={handleSend}
          disabled={!hasResult || loading}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-slate-300"
        >
          发送
        </button>
      </div>
    </div>
  );
}