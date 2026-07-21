import type { HistoryRecord } from "../history";

interface Props {
  records: HistoryRecord[];
  selectedId: string | null;
  onSelect: (r: HistoryRecord) => void;
  onDelete: (id: string) => void;
}

export default function HistoryPanel({ records, selectedId, onSelect, onDelete }: Props) {
  if (records.length === 0) return null; // 没历史就不显示

  return (
    <div className="mb-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-2 font-semibold text-slate-800">🕓 历史记录</div>
      <div className="space-y-2">
        {records.map((r) => (
          <div
            key={r.id}
            className={
              "flex items-center justify-between rounded-lg border px-3 py-2 " +
              (r.id === selectedId ? "border-blue-300 bg-blue-50" : "border-slate-100 bg-slate-50")
            }
          >
            <button onClick={() => onSelect(r)} className="min-w-0 flex-1 text-left hover:text-blue-600">
              <div className="truncate text-sm font-medium text-slate-700">{r.title}</div>
              <div className="text-xs text-slate-400">{new Date(r.createdAt).toLocaleString()}</div>
            </button>
            <button onClick={() => onDelete(r.id)} className="ml-2 shrink-0 text-xs text-slate-400 hover:text-red-500">
              删除
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}