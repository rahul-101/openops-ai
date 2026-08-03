export type IncidentSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
export type IncidentStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED"
export type IncidentCategory = "incident" | "agent" | "execution"

export interface Incident {
  id: string
  title: string
  description: string
  severity: IncidentSeverity
  status: IncidentStatus
  source: string
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  page: number
  size: number
  total_items: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface CreateIncidentInput {
  title: string
  description: string
  severity: IncidentSeverity
  source: string
}

export interface AIResponse {
  summary: string
  severity: string
  category: string
  probable_cause: string
  recommendation: string
  confidence: number
  provider: string
  model: string
  input_tokens: number
  output_tokens: number
  processing_time_ms: number
}

export interface DashboardSnapshot {
  generated_at: string
  incidents: {
    total_incidents: number
    resolved_incidents: number
    open_incidents: number
    auto_resolution_rate: number
    average_resolution_time_s: number
  }
  ai: {
    agent_success_rate: number
    total_agent_runs: number
    model_usage: Record<string, number>
    input_tokens: number
    output_tokens: number
    cost_usd: number
  }
  execution: {
    successful_actions: number
    failed_actions: number
    rollback_count: number
  }
}

export interface OperationsEvent {
  event_id: string
  type: string
  category: IncidentCategory
  incident_id: string
  agent: string
  action: string
  status: string
  duration_ms: number
  metadata: Record<string, unknown>
  timestamp: string
}

export interface Execution {
  execution_id: string
  incident_id: string
  agent?: string
  status?: string
  started_at?: string
  completed_at?: string | null
  duration_ms?: number
  metadata?: Record<string, unknown>
}

export interface ExecutionsResponse {
  summary: Record<string, unknown>
  executions: Execution[]
}

export interface AiActivitySnapshot {
  active_agents: number
  current_tasks: number
  completed_actions: number
  failures: number
}

export interface ProviderHealth {
  provider: string
  status: string
  circuit_state: string
  consecutive_failures: number
  consecutive_successes: number
  last_success: string | null
  last_failure: string | null
  retry_after: string | null
  last_error: string | null
  updated_at: string
}

export interface ProviderMetrics {
  provider: string
  total_requests: number
  successful_requests: number
  failed_requests: number
  success_rate: number
  failure_rate: number
  average_response_time_ms: number
  last_response_time_ms: number | null
  last_error: string | null
  updated_at: string
}

export interface ProviderMetadata {
  name: string
  display_name: string
  model: string
  priority: number
  input_cost_per_1k_tokens: number
  output_cost_per_1k_tokens: number
  max_context_tokens: number
  capabilities: string[]
  enabled: boolean
}

export interface AgentAnalytics {
  agent: string
  total_runs: number
  success_rate: number
  failed_runs: number
  average_latency_ms: number
}

export interface ProviderPerformance {
  provider: string
  total_calls: number
  success_rate: number
  average_latency_ms: number
}

export interface ModelStats {
  total_requests: number
  total_tokens: number
  total_cost_usd: number
  average_latency_ms: number
  providers: Record<string, { requests: number; cost_usd: number; tokens: number }>
}

export interface ReasoningReport {
  incident_id: string
  decision: string
  confidence: number
  risk: string
  validated: boolean
  reasoning: string[]
  evidence: string[]
  alternatives: string[]
  explanation: Record<string, unknown>
  agents_involved: string[]
  model_selection: Record<string, unknown>
  history_id: string
}

export interface LifecycleRecord {
  incident_id: string
  status: string
  servicenow_updated: boolean
  learning_recorded: boolean
  steps: LifecycleStep[]
}

export interface LifecycleStep {
  stage: string
  status: string
  details: string
}

export interface WorkflowState {
  incident_id: string
  workflow_id: string
  workflow_status: string
  current_step: string | null
  agent_history: AgentHistoryEntry[]
  recommendations: string[]
  execution_result: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface AgentHistoryEntry {
  agent: string
  status: string
  output: Record<string, unknown>
  error: string | null
  duration_ms: number
  executed_at: string
}

export interface Playbook {
  name: string
  description: string
  version: string
  steps: PlaybookStep[]
}

export interface PlaybookStep {
  name: string
  tool: string
  action: string
  risk_level: string
}

export interface AlertDecision {
  incident_id: string
  summary: string
  category: string
  probable_cause: string
  recommendation: string
  confidence: number
  playbook: string
  can_auto_execute: boolean
  actions: DecisionAction[]
}

export interface DecisionAction {
  tool: string
  action: string
  risk_level: string
  decision: string
  approved: boolean
}

export interface KnowledgeDocument {
  id: string
  title: string
  content: string
  type: string
  source: string | null
  metadata: Record<string, unknown>
  created_at: string | null
}

export interface AuditEntry {
  id: string
  user?: string
  action?: string
  incident_id?: string
  decision?: string
  timestamp?: string
}

export type ApprovalStatus = "pending" | "approved" | "rejected" | "executed"

export interface Approval {
  id: string
  tool_name: string
  parameters: Record<string, unknown>
  context: Record<string, unknown>
  status: ApprovalStatus
  requested_by: string | null
  approved_by: string | null
  reason: string | null
  result: Record<string, unknown> | null
  created_at: string
  updated_at: string
}