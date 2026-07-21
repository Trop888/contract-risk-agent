// 风险等级：只能是这三个值之一（TypeScript 的联合类型）
export type RiskLevel = "高" | "中" | "低";

// 单条风险（对应后端的 RiskItem）
export interface RiskItem {
  risk_type: string;
  level: RiskLevel;
  description: string;
  clause?: string | null;      // ? 表示可选字段
  suggestion?: string | null;
  legal_basis?: string | null;
}

// 完整分析结果（对应后端的 ContractAnalysisResult）
export interface ContractAnalysisResult {
  is_valid: boolean;
  summary: string;
  risk_items: RiskItem[];
  overall_risk: RiskLevel;
  overall_conclusion: string;
  contract_text?: string | null;
}

// 对话消息
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}