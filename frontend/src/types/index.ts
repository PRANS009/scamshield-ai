export type Kind='url'|'message'|'email'|'shopping'|'internship'|'job'|'contract'|'qr';
export interface Source {id:string;title:string;url:string;snippet:string;retrieved_at:string;source_type:string;stance:string;query:string}
export interface Report {report_id:string;analysis_type:string;created_at:string;risk_score:number;risk_level:string;evidence_confidence:string;research_status:string;research_errors:string[];red_flags:{code:string;label:string;points:number;explanation:string}[];verified_facts:string[];unverified_claims:string[];supporting_evidence:string[];contradictory_evidence:string[];sources:Source[];recommendations:string[];extracted:Record<string,unknown>;quality:null|{score:number;criteria:Record<string,boolean>;meaning:string};workflow:{agent:string;status:string;detail:string}[];summary:string;ai_status:string;ai_explanation:null|{answer:string;source_ids:string[];uncertainty:string};limitations:string[]}
export interface Job {id:string;title:string;company:string;location:string;description:string;posted_at:string;salary:string;verification:string;links:{title:string;url:string}[]}
export interface Application {id:string;title:string;company:string;url:string;status:string;notes:string;deadline:string}

export interface ToolExecution {
  tool: string;
  status: string;
  [key: string]: any;
}

export interface RiskAssessment {
  level: 'Low' | 'Moderate' | 'High' | 'Insufficient Evidence' | string;
  score: number;
  reasons: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tools_executed?: ToolExecution[];
  risk_level?: string;
  risk_score?: number;
  findings?: string[];
  evidence_leads?: Source[];
  uncertainty?: string;
  suggested_prompts?: string[];
  report?: Report;
}

export interface ChatResponse {
  session_id: string;
  assistant_message: string;
  tools_executed: ToolExecution[];
  findings: string[];
  evidence_sources: Source[];
  risk_assessment: RiskAssessment | null;
  uncertainty: string;
  suggested_next_steps: string[];
  suggested_prompts: string[];
  report: Report | null;
  mode: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  research_consent?: boolean;
  ai_consent?: boolean;
  company?: string;
  official_domain?: string;
  recruiter_email?: string;
}

