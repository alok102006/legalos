export interface ContractSummary {
  id: string;
  document_id: string;
  title: string | null;
  counterparty_name: string | null;
  status: 'processing' | 'analyzed' | 'failed';
  created_at: string;
  risk_clause_count: number;
  high_risk_count: number;
}

export interface NegotiationSuggestion {
  id: string;
  clause_id: string;
  suggestion_text: string;
  created_at: string;
}

export interface Clause {
  id: string;
  contract_id: string;
  clause_index: number;
  raw_text: string;
  summary: string | null;
  risk_type: 'penalty' | 'lock_in' | 'indemnity' | 'termination' | 'none';
  risk_score: number;
  qdrant_point_id: string | null;
  created_at: string;
  suggestions: NegotiationSuggestion[];
}

export interface ContractDetail {
  id: string;
  document_id: string;
  title: string | null;
  counterparty_name: string | null;
  status: 'processing' | 'analyzed' | 'failed';
  created_at: string;
  clauses: Clause[];
}
