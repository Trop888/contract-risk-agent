import type { ContractAnalysisResult, RiskLevel } from "../types";
import { downloadReport } from "../api";

const LEVEL_COLOR: Record<RiskLevel, string> = { 高: "#DC2626", 中: "#D97706", 低: "#16A34A" };
const LEVEL_EMOJI: Record<RiskLevel, string> = { 高: "🔴", 中: "🟠", 低: "🟢" };

export default function ResultView({ result }: { result: ContractAnalysisResult }) {
  if (!result.is_valid) {
    return (
      <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        ⚠️ 无法进行有效审查：{result.summary}
      </div>
    );
  }

  const high = result.risk_items.filter((it) => it.level === "高").length;
  const mid = result.risk_items.filter((it) => it.level === "中").length;
  const low = result.risk_items.filter((it) => it.level === "低").length;
  const cards = [
    { value: result.overall_risk, label: "整体风险", color: LEVEL_COLOR[result.overall_risk] },
    { value: String(high), label: "高风险", color: "#DC2626" },
    { value: String(mid), label: "中风险", color: "#D97706" },
    { value: String(low), label: "低风险", color: "#16A34A" },
  ];

  return (
    <div className="mt-5 space-y-5">
      {result.errors && result.errors.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          ⚠️ 本次分析部分环节降级，报告可能不完整：
          <ul className="mt-1 list-disc pl-5">
            {result.errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-4 gap-3">        
        {cards.map((c) => (
          <div key={c.label} className="rounded-xl px-3 py-4 text-center text-white" style={{ background: c.color }}>
            <div className="text-2xl font-bold">{c.value}</div>
            <div className="text-xs opacity-90">{c.label}</div>
          </div>
        ))}
      </div>

      <div className="rounded-lg bg-slate-50 px-5 py-4" style={{ borderLeft: `5px solid ${LEVEL_COLOR[result.overall_risk]}` }}>
        <div className="mb-1 text-xs text-slate-500">📋 总体结论</div>
        <div className="text-sm leading-relaxed text-slate-800">{result.overall_conclusion}</div>
      </div>

      <button onClick={() => downloadReport(result)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
        📥 下载 Word 报告
      </button>

      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="mb-2 font-semibold text-slate-800">📝 合同摘要</div>
        <p className="text-sm leading-relaxed text-slate-600">{result.summary}</p>
      </div>

      <div>
        <h3 className="mb-3 font-semibold text-slate-800">🔍 发现 {result.risk_items.length} 项风险</h3>
        <div className="space-y-3">
          {result.risk_items.map((item, i) => (
            <details key={i} className="rounded-xl border border-slate-200 bg-white p-4">
              <summary className="flex cursor-pointer flex-wrap items-center gap-2 font-medium text-slate-800">
                <span>{LEVEL_EMOJI[item.level]} 风险 {i + 1}：{item.risk_type}（{item.level}风险）</span>
                {item.source && (
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-normal ${
                      item.source === "规则引擎"
                        ? "bg-indigo-100 text-indigo-700"
                        : "bg-sky-100 text-sky-700"
                    }`}
                  >
                    {item.source === "规则引擎" ? "⚡规则引擎" : "🤖AI审查"}
                  </span>
                )}
              </summary>              <div className="mt-3 space-y-2 text-sm text-slate-600">
                <p><span className="font-medium text-slate-700">描述：</span>{item.description}</p>
                {item.clause && <p><span className="font-medium text-slate-700">相关条款：</span>{item.clause}</p>}
                {item.suggestion && <p><span className="font-medium text-slate-700">💡 修改建议：</span>{item.suggestion}</p>}
                {item.legal_basis && <p><span className="font-medium text-slate-700">⚖️ 法律依据：</span>{item.legal_basis}</p>}
              </div>
            </details>
          ))}
        </div>
      </div>
    </div>
  );
}