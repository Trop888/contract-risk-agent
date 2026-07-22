export type RiskLevel = "高" | "中" | "低";

export interface RiskItem {
  risk_type: string;
  level: RiskLevel;
  description: string;
  clause?: string | null;    
  suggestion?: string | null;
  legal_basis?: string | null;
  source?: string;
}

export interface ContractAnalysisResult {
  is_valid: boolean;
  summary: string;
  risk_items: RiskItem[];
  overall_risk: RiskLevel;
  overall_conclusion: string;
  contract_text?: string | null;
  errors?: string[];
}

// 对话消息
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}