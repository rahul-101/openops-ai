<div align="center">

<h1 style="font-size:42px;margin:32px 0 8px;background:linear-gradient(90deg,#00e5ff,#ff2ec4);-webkit-background-clip:text;background-clip:text;color:transparent">🏗️ ARCHITECTURE</h1>
<p style="color:#8b93b0;letter-spacing:3px;text-transform:uppercase;font-size:13px">Deep-Dive System Design</p>

</div>

---

# 🏗️ OpenOps AI — Architecture Guide

> A layered, clean-architecture backend for autonomous incident response, powered by a multi-agent AI core and surfaced through a real-time command center.

---

## 1. System Overview

```
                       ┌─────────────────────────────────────────────────┐
                       │                 CLIENTS / EXTERNAL               │
                       │      Alert sources · UIs · Slack/Teams · SIEM    │
                       └──────────────────────┬──────────────────────────┘
                                              │  HTTP (REST) · SSE
                       ┌──────────────────────▼──────────────────────────┐
                       │                     FASTAPI                      │
                       │       12 routers · 60+ endpoints · middleware    │
                       └──────────────────────┬──────────────────────────┘
                                              │
        ┌─────────────────────────────────────┼─────────────────────────────┐
        │             APPLICATION LAYER        │                             │
        │  Services ─ Agent framework ─ Workflows ─ Orchestration            │
        ├─────────────────────────────────────┼─────────────────────────────┤
        │           INFRASTRUCTURE LAYER      │                             │
        │  AI Gateway │ AIOps │ Reasoning │ Command Center                  │
        │  Governance │ Knowledge │ Learning │ Reliability │ Tools          │
        │  Monitoring │ Persistence (Mongo / in-memory)                    │
        └─────────────────────────────────────┴─────────────────────────────┘
```

---

## 2. Layered Architecture

### 🎯 Presentation — `app/api`

| Router | Prefix | Purpose |
|---|---|---|
| `v1/health.py` | — | Liveness, welcome, error-demo |
| `v1/incidents.py` | `/incidents` | Incident CRUD |
| `v1/incident_analysis.py` | `/incidents` | AI incident analysis |
| `routes/aiops.py` | `/aiops` | Autonomous operations |
| `routes/reasoning.py` | `/reasoning` | Decision intelligence |
| `routes/reliability.py` | `/reliability` | Resilience suite |
| `routes/governance.py` | `/governance` | Security & compliance |
| `routes/optimization.py` | `/optimization` | Self-optimization |
| `routes/command_center.py` | — | Real-time ops (SSE) |
| `routes/workflow.py` | `/incidents/{id}/workflow` | Agent pipeline |
| `routes/ai_monitoring.py` | `/ai/providers` | Provider health |
| `routes/metrics.py` | — | Prometheus exposition |

### ⚙️ Application — `app/application`

- **Services** — `IncidentService`, `IncidentAnalysisService`, `ProviderMonitoringService`.
- **Agents** — `Agent` ABC, `AgentRegistry`, `AgentContext`, `AgentResult` + `AgentStatus`.
- **Orchestration** — `AgentOrchestrator` (runs registered agents).
- **Workflows** — `WorkflowEngine` (status/step/checkpoint model) + `IncidentWorkflow` (triage → analysis → recommendation).
- **DTOs & Mappers** — request/response models, `IncidentMapper`.

### 🧱 Domain — `app/domain`

- `Incident` entity — severity (`LOW→CRITICAL`) and status (`OPEN/IN_PROGRESS/RESOLVED`).
- `IncidentQuery` — pagination + filters + sorting.
- `Page[T]` — generic pagination.
- `IncidentRepository` — repository interface (DI-swappable implementations).

### 🏭 Infrastructure — `app/infrastructure`

See [§3 Core Subsystems](#3-core-subsystems) below.

---

## 3. Core Subsystems

### 3.1 AI Gateway — `app/infrastructure/ai`

```
Providers ──▶ Registry ──▶ Health (circuit breaker) ──▶ Router (failover)
     │             │               │                        │
   Gemini      metadata       CLOSED/HALF_OPEN/OPEN      cost-aware
   OpenRouter  capabilities    threshold=3 failures     PriorityRoutingPolicy
```

- **Providers** — `GeminiProvider`, `OpenRouterProvider` behind a common interface.
- **Registry** — provider metadata: model, cost per 1k tokens, priority, context window.
- **Health** — `ProviderHealthService` with a circuit breaker (`FAILURE_THRESHOLD=3`).
- **Routing** — `RoutingEngine` + `ProviderScorer` (weights: latency `0.40` · reliability `0.35` · cost `0.15` · priority `0.10`) + `PriorityRoutingPolicy` + `AIRouter` failover.

### 3.2 AIOps — `app/infrastructure/aiops`

```
RawAlert ─▶ EventIngestionEngine ─▶ NormalizedEvent
                                        │
                   ┌────────────────────┼────────────────────┐
                   ▼                    ▼                    ▼
          DecisionEngine         PlaybookEngine        MultiAgentRunner
        (analysis+actions)       (YAML playbooks)      (5 agents)
                   │                    │                    │
                   └──────────┬─────────┴────────────────────┘
                              ▼
                    IncidentLifecycleOrchestrator
                    INGESTED → ANALYZED → EXECUTE → VERIFIED/FAILED
                              ▼
                    RiskBasedExecutor (auto / approval / blocked)
```

### 3.3 Reasoning — `app/infrastructure/reasoning`

```
NormalizedEvent ─▶ ReasoningOrchestrator
                    ├─ MultiAgentReasoningRunner (IncidentAnalysis, RCA, Verification, Decision)
                    ├─ DecisionConfidenceEngine (confidence + risk)
                    ├─ DecisionExplainer (rationale)
                    ├─ SelfVerificationLayer (min confidence 0.70)
                    ├─ DynamicModelSelector (complexity → flash/pro)
                    └─ ReasoningHistoryStore (persistence)
```

### 3.4 Command Center — `app/infrastructure/command_center`

```
  any publisher ─▶ EventPublisher ─┬─▶ async streams (SSE)
                                  ├─▶ sync listeners
                                  └─▶ bounded history
                                          │  OperationsCommandCenter._on_event
        ┌─────────────────────────────────┼───────────────────────────┐
        ▼                                 ▼                           ▼
  IncidentTimeline                  ActivityFeed               OperationsDashboard
  (per-incident)             (agents/tasks/actions)     (incident·AI·execution KPIs)
                                              ExecutionMonitor (running/completed/failed)
```

### 3.5 Governance — `app/infrastructure/governance`

| Service | Responsibility |
|---|---|
| `RbacService` | Roles: admin / operator / analyst / viewer |
| `ApprovalPolicyEngine` | Risk-level action registry (e.g. `kubernetes.restart` → MEDIUM) |
| `AuditLogService` | Immutable audit trail (user/action/incident/decision) |
| `DataPrivacyService` | PII masking via regex |
| `ModelGovernanceService` | Model usage + cost statistics |
| `PromptRegistry` | Versioned, governed prompts |

### 3.6 Knowledge / RAG — `app/infrastructure/knowledge`

```
Documents ─▶ IngestionPipeline ─▶ EmbeddingService ─▶ VectorRepository
                          (chunk/overlap)   (hashing | Gemini 004)  (memory | Atlas $vectorSearch)
                                                    │
                                            KnowledgeBaseService
                                                    │
                                             KnowledgeRetrievalAgent ─▶ AgentRegistry
```

### 3.7 Reliability — `app/infrastructure/reliability`

| Module | Purpose |
|---|---|
| `WorkflowRecovery` | Checkpoint + resume long workflows |
| `RemediationRollback` | Rollback records + retrieval |
| `RootCauseGraph` | Weighted RCA factor ranking |
| `DependencyIntelligence` | Service dependency impact |
| `IncidentCorrelation` | Duplicate detection |
| `BusinessImpactAnalysis` | SEV + SLA scoring |
| `ChaosTestingSimulator` | Failure injection + recovery rate |

### 3.8 Tools — `app/infrastructure/tools`

- **Core** — `Tool` ABC, `ToolRegistry`, `ToolExecutor`, `ApprovalWorkflow`, `HttpTransport`.
- **Integrations** — ServiceNow, Jira, AWS, Azure, Kubernetes, Slack, Teams, Database.
- **Risk gating** — mutating actions route through the approval workflow.

### 3.9 Learning — `app/infrastructure/learning`

Feedback → Evaluation → RoutingOptimizer → PromptOptimizer → AgentAnalytics → CostOptimizer (cheapest capable model).

### 3.10 Observability — `app/infrastructure/monitoring` + `app/core`

- **Prometheus** — counters (requests/success/failure/tokens/cost), latency histogram, circuit-state gauge; exposition at `GET /metrics`.
- **Logging** — structlog JSON + request-id middleware (`X-Request-ID`).
- **Exceptions** — `OpenOpsException` hierarchy mapped to HTTP status (404/409/500).

---

## 4. Dependency Injection

`app/infrastructure/dependencies.py` exposes **47 cached providers** (`@lru_cache` singletons):

```
Repos/Services        IncidentRepository, IncidentService
AI Gateway            GeminiProvider, OpenRouterProvider, Registry, Health, Metrics,
                      Scorer, RoutingEngine, AIRouter, Bootstrap
Agents/Workflow       AgentRegistry, AgentOrchestrator, WorkflowEngine, IncidentWorkflow
Knowledge             EmbeddingService, VectorRepository, KnowledgeBaseService,
                      IngestionPipeline, IncidentMemoryService, RetrievalAgent
Tools                 ApprovalWorkflow, ToolRegistry, ToolExecutor
Governance            RbacService, AuditLogService, ApprovalPolicyEngine,
                      PromptRegistry, ModelGovernanceService, DataPrivacyService
Learning              FeedbackEngine, EvaluationEngine, RoutingOptimizer,
                      PromptOptimizer, AgentAnalytics, CostOptimizer
AIOps                 IngestionEngine, RiskBasedExecutor, PlaybookEngine,
                      DecisionEngine, MultiAgentRunner, LifecycleOrchestrator
Reliability           WorkflowRecovery, RemediationRollback, RootCauseGraph,
                      DependencyIntelligence, IncidentCorrelation,
                      BusinessImpactAnalysis, ChaosTestingSimulator
Reasoning             ConfidenceEngine, Explainer, VerificationLayer, HistoryStore,
                      ModelSelector, ReasoningRunner, ReasoningOrchestrator
Command Center        EventPublisher, IncidentTimeline, ActivityFeed, ExecutionMonitor,
                      OperationsDashboard, OperationsCommandCenter
```

Persistence is **runtime-switchable** via `REPOSITORY_TYPE=mongo|memory` for incidents, vectors, and incident memory.

---

## 5. Request Lifecycle (Example: Autonomous Response)

```
1. POST /aiops/lifecycle/run
        └─ IngestionEngine.normalize(alert)
2. DecisionEngine.decide(event, playbook)
        └─ PlaybookEngine.find(event)      # YAML match
3. MultiAgentRunner.run(context)            # 5 agents
4. RiskBasedExecutor gates tool actions
5. ToolExecutor executes approved actions
6. Verification validates resolution
7. LifecycleOrchestrator emits CommandCenterEvent
        └─ EventPublisher fan-out
             ├─ IncidentTimeline.record
             ├─ ActivityFeed.update
             ├─ ExecutionMonitor.complete
             └─ SSE stream ─▶ /operations/events/stream
```

---

## 6. Data & Persistence

| Concern | Default | Mongo Option |
|---|---|---|
| Incidents | in-memory | `mongo_incident_repository` |
| Vectors | in-memory cosine | Atlas `$vectorSearch` |
| Incident memory | in-memory | mongo implementation |
| Reasoning history | in-memory | — |
| Audit log | in-memory | — |

---

<div align="center">
<strong style="color:#00ff9c">471 tests green</strong> · <span style="color:#8b93b0">OpenOps AI Architecture · v0.3.0</span>
</div>
