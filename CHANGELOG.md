<div align="center">

<style>
:root{
  --bg:#05060f;--panel:#0b0f1e;--border:#1a2340;
  --cyan:#00e5ff;--magenta:#ff2ec4;--green:#00ff9c;
  --violet:#a855f7;--amber:#ffb86c;--red:#ff5470;
  --text:#e6e9f5;--muted:#8b93b0;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;line-height:1.6}
h1,h2,h3{color:var(--text)}
h2{border-bottom:1px solid var(--border);padding-bottom:8px;margin-top:40px}
h2::before{content:"◆ ";color:var(--cyan);text-shadow:0 0 8px var(--cyan)}
a{color:var(--cyan)}
code{background:#131a33;border:1px solid var(--border);border-radius:6px;padding:2px 6px;color:var(--green)}
pre{background:#0a0e1f;border:1px solid var(--border);border-radius:12px;padding:16px;overflow-x:auto}
table{border-collapse:collapse;width:100%;margin:12px 0}
th,td{border:1px solid var(--border);padding:10px 14px;text-align:left}
th{background:#0f1630;color:var(--cyan);text-transform:uppercase;font-size:.78em;letter-spacing:1px}
blockquote{border-left:3px solid var(--cyan);background:#0b0f1e;padding:8px 16px;color:var(--muted)}
hr{border:none;height:1px;background:linear-gradient(90deg,var(--cyan),var(--magenta),transparent)}
</style>

<h1 style="font-size:42px;margin:32px 0 8px;background:linear-gradient(90deg,#00ff9c,#00e5ff);-webkit-background-clip:text;background-clip:text;color:transparent">📝 CHANGELOG</h1>
<p style="color:#8b93b0;letter-spacing:3px;text-transform:uppercase;font-size:13px">Release History</p>

</div>

---

# 📝 Changelog

All notable changes to **OpenOps AI** are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [0.3.0] — In Development

### Added — Phase 20 · Real-Time Operations Command Center

- ⚡ **`EventPublisher`** — thread-safe in-memory pub/sub with async SSE streams (15s keep-alive), bounded history, filtered queries.
- 🕰️ **`IncidentTimeline`** — per-incident chronological event timeline.
- 🤖 **`ActivityFeed`** — live tracking of active agents, current tasks, completed actions, failures.
- 📊 **`ExecutionMonitor`** — running/completed/failed executions with duration + error capture.
- 🎛️ **`OperationsDashboard`** — aggregated incident / AI / execution KPIs.
- 🏢 **`OperationsCommandCenter`** — facade wiring publisher → timeline/activity/dashboard.
- 🔌 **New API** under `/operations`: `GET /operations/events/stream` (SSE), `/operations/events`, `/operations/dashboard`, `/operations/executions`, `/operations/metrics/{incidents,ai,execution}`, `GET /ai/activity`, `GET /incidents/{id}/timeline`.
- 🔗 **Publisher hooks** in `ReasoningOrchestrator` and `IncidentLifecycleOrchestrator` emit events automatically.

### Added — Phase 19 · Advanced AI Reasoning

- 🧠 **`ReasoningOrchestrator`** — multi-agent reasoning pipeline (IncidentAnalysis → RCA → Verification → Decision).
- 🎯 **`DecisionConfidenceEngine`** — confidence scoring + risk classification.
- 💬 **`DecisionExplainer`** — human-readable explanation generation.
- 🔍 **`SelfVerificationLayer`** — pre-execution validation (min confidence 0.70).
- 🧮 **`DynamicModelSelector`** — task-complexity → model-tier routing.
- 🗄️ **`ReasoningHistoryStore`** — per-incident reasoning records.
- 🔌 **New API** under `/reasoning`: `reason`, `confidence`, `explain`, `verify`, `model/select`, `model/classify`, `model/models`, `history`, `history/{incident_id}`.

### Added — Phase 18 · Reliability & Resilience

- ♻️ **`WorkflowRecovery`** — checkpoint/resume for long-running workflows.
- ↩️ **`RemediationRollback`** — structured rollback records.
- 🌳 **`RootCauseGraph`** — weighted root-cause factor ranking.
- 🧭 **`DependencyIntelligence`** — service dependency impact analysis.
- 🔗 **`IncidentCorrelation`** — duplicate/related incident detection.
- 💼 **`BusinessImpactAnalysis`** — SEV classification + SLA impact.
- 🌀 **`ChaosTestingSimulator`** — failure injection + autonomous recovery-rate.
- 🔌 **New API** under `/reliability`: workflows, rollback, rca, dependencies, correlate, impact, chaos.

---

## [0.2.0] — Phases 8–17

### Added — Platform Expansion

- 🔌 **AIOps** — alert ingestion, `AutonomousDecisionEngine`, YAML playbook engine, `RiskBasedExecutor` (auto/approval/blocked), 5-agent runner, `IncidentLifecycleOrchestrator`. API under `/aiops`.
- 🔧 **Tool fabric** — `Tool` ABC, `ToolRegistry`, `ToolExecutor`, approval workflow, HTTP transport; ServiceNow, Jira, AWS, Azure, Kubernetes, Slack, Teams, Database integrations.
- 🏛️ **Governance** — RBAC (admin/operator/analyst/viewer), audit log, approval policy engine, data privacy (PII masking), model governance, versioned prompt registry. API under `/governance`.
- 📚 **Knowledge / RAG** — document ingestion pipeline, embedding service (hashing + Gemini `text-embedding-004`), vector repository (in-memory cosine + Atlas `$vectorSearch`), incident memory, retrieval agent.
- 🧮 **Learning** — feedback engine, evaluation engine, routing optimizer, prompt optimizer, agent analytics, cost optimizer. API under `/optimization`.
- 🤖 **Agent framework** — `Agent` ABC, `AgentRegistry`, `AgentOrchestrator`, `WorkflowEngine`, `IncidentWorkflow` (triage → analysis → recommendation). API under `/incidents/{id}/workflow`.
- 📊 **Observability** — Prometheus metrics, provider health service, metrics registry, cost estimation. API under `/metrics` and `/ai/providers`.

---

## [0.1.0] — Phases 1–7

### Added — Foundation

- 🚀 FastAPI application shell + lifespan bootstrap.
- ⚙️ **Configuration** — pydantic-settings `Settings`, `.env` support.
- 🧩 **Domain** — `Incident` entity (severity/status enums), `IncidentQuery`, generic `Page[T]`, `IncidentRepository` ABC.
- 🏗️ **Application** — `IncidentService` (CRUD), `IncidentMapper`, DTO request/response models.
- 🖥️ **API** — `/health`, `/`, `/demo-error`, full `/incidents` CRUD, `POST /incidents/analyze`.
- 🛡️ **Error handling** — `OpenOpsException` hierarchy + global handlers (404/409/500).
- 📝 **Logging** — structlog JSON logging + request-id middleware.
- 💾 **Persistence** — in-memory + MongoDB repositories (switchable via `REPOSITORY_TYPE`).

---

<div align="center">
<strong style="color:#00ff9c">471 tests passing</strong> · <span style="color:#8b93b0">See NEXT_TASKS.md for the roadmap ahead</span>
</div>
