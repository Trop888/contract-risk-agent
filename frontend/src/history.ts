import type { ChatMessage, ContractAnalysisResult } from "./types";

const KEY = "contract_history"; // 存储的键名

export interface HistoryRecord {
  id: string;              // 唯一ID（用时间戳）
  title: string;           // 显示标题（文件名）
  createdAt: number;       // 创建时间戳
  result: ContractAnalysisResult;
  messages: ChatMessage[]; // 该记录的对话历史
}

// 读取全部历史
export function loadHistory(): HistoryRecord[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

// 新增一条（返回更新后的列表），最多保留20条
export function addHistory(result: ContractAnalysisResult, title: string): HistoryRecord[] {
  const record: HistoryRecord = {
    id: String(Date.now()),
    title,
    createdAt: Date.now(),
    result,
    messages: [], // 新记录对话为空
  };
  const next = [record, ...loadHistory()].slice(0, 20);
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

// 删除一条（返回更新后的列表）
export function removeHistory(id: string): HistoryRecord[] {
  const next = loadHistory().filter((r) => r.id !== id);
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

// 更新某条记录的对话历史（返回更新后的列表）
export function updateHistoryMessages(id: string, messages: ChatMessage[]): HistoryRecord[] {
  const next = loadHistory().map((r) => (r.id === id ? { ...r, messages } : r));
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}