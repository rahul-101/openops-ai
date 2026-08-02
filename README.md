<div align="center">

<!-- ============================= HERO ============================= -->

<div align="center" style="padding:48px 16px 24px">

<h1 style="
  font-size:56px;line-height:1.1;margin:0 0 8px;letter-spacing:-1px;
  background:linear-gradient(90deg,#00e5ff,#ff2ec4,#a855f7,#00e5ff);
  background-size:200% 100%;
  -webkit-background-clip:text;background-clip:text;color:transparent;
  animation:flow 6s linear infinite;
">
  ⚡ OPENOPS AI
</h1>

<p style="font-size:20px;color:#8b93b0;margin:8px 0 20px;letter-spacing:4px;text-transform:uppercase">
  Enterprise Autonomous Incident Response Platform
</p>

<p style="margin:0 0 24px">
  <span style="display:inline-block;padding:6px 18px;margin:4px;border-radius:999px;font-size:13px;letter-spacing:1px;border:1px solid rgba(0,229,255,.5);color:#00e5ff;text-shadow:0 0 8px rgba(0,229,255,.6)">FASTAPI</span>
  <span style="display:inline-block;padding:6px 18px;margin:4px;border-radius:999px;font-size:13px;letter-spacing:1px;border:1px solid rgba(255,46,196,.5);color:#ff2ec4;text-shadow:0 0 8px rgba(255,46,196,.6)">GOOGLE ADK</span>
  <span style="display:inline-block;padding:6px 18px;margin:4px;border-radius:999px;font-size:13px;letter-spacing:1px;border:1px solid rgba(0,255,156,.5);color:#00ff9c;text-shadow:0 0 8px rgba(0,255,156,.6)">GEMINI</span>
  <span style="display:inline-block;padding:6px 18px;margin:4px;border-radius:999px;font-size:13px;letter-spacing:1px;border:1px solid rgba(168,85,247,.5);color:#a855f7;text-shadow:0 0 8px rgba(168,85,247,.6)">MONGODB ATLAS</span>
  <span style="display:inline-block;padding:6px 18px;margin:4px;border-radius:999px;font-size:13px;letter-spacing:1px;border:1px solid rgba(255,184,108,.5);color:#ffb86c;text-shadow:0 0 8px rgba(255,184,108,.6)">PROMETHEUS</span>
</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-00e5ff?style=for-the-badge&labelColor=0b0f1e">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.140-ff2ec4?style=for-the-badge&labelColor=0b0f1e">
  <img alt="Tests" src="https://img.shields.io/badge/tests-471%20passing-00ff9c?style=for-the-badge&labelColor=0b0f1e">
  <img alt="Status" src="https://img.shields.io/badge/status-under%20development-ffb86c?style=for-the-badge&labelColor=0b0f1e">
</p>

</div>

<!-- ============================= TAGLINE ============================= -->

<blockquote align="center" style="max-width:800px;margin:0 auto 24px">
  <p style="margin:0"><strong style="color:#00e5ff">Detect.</strong> <strong style="color:#ff2ec4">Reason.</strong> <strong style="color:#a855f7">Act.</strong> <strong style="color:#00ff9c">Recover.</strong> — An autonomous platform that ingests alerts, runs multi-agent AI reasoning, executes approved remediations, and streams everything to a real-time operations command center.</p>
</blockquote>

</div>

---

# 🌌 OpenOps AI — Enterprise Autonomous Incident Response

> **The platform** autonomously detects incidents, reasons over them with a fleet of specialized AI agents, executes risk-gated remediation, learns from every outcome, and surfaces the entire journey through a live operations dashboard.

---

## 🚀 Highlights

| | |
|---|---|
| 🤖 **5-stage AIOps lifecycle** | Ingest → Analyze → Decide → Execute → Verify, orchestrated end-to-end |
| 🧠 **Multi-agent reasoning** | Incident analysis, RCA, verification, and decision agents with confidence + explanation + self-verification |
| 🛡️ **Risk-gated execution** | Low-risk actions auto-run; medium requires approval; high is blocked (RiskBasedExecutor) |
| ⚡ **Real-time command center** | SSE event streaming, incident timelines, activity feed, execution monitor, ops dashboard |
| 🔁 **Reliability & resilience** | Workflow recovery, remediation rollback, root-cause graphs, dependency intelligence, chaos testing |
| 🏛️ **Governance built-in** | RBAC, audit log, approval policies, data privacy (PII masking), model & prompt governance |
| 📚 **Knowledge & memory** | RAG over incident history, vector search (in-memory cosine or Atlas `$vectorSearch`) |
| 🧮 **Self-optimization** | Feedback engine, evaluation engine, routing optimizer, prompt optimizer, cost optimizer |
| 📊 **Observability** | Prometheus metrics, provider health with circuit breakers, structlog JSON logging, request tracing |
| 🔌 **Integration fabric** | ServiceNow, Jira, AWS, Azure, Kubernetes, Slack, Teams, Database tooling |

---

## 🧱 Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER (FastAPI)                              │
│  /incidents  /aiops  /reasoning  /reliability  /governance  /optimization     │
│  /operations (SSE)  /metrics  /workflow  /ai/providers                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                            APPLICATION LAYER                                  │
│  Agent framework · AgentOrchestrator · WorkflowEngine · IncidentWorkflow      │
│  IncidentService · IncidentAnalysisService · ProviderMonitoringService       │
├──────────────────────────────────────────────────────────────────────────────┤
│                          INFRASTRUCTURE LAYER                                 │
│  AI Gateway (Gemini/OpenRouter + router + circuit breaker)                    │
│  AIOps lifecycle · Reasoning pipeline · Command Center                        │
│  Governance · Knowledge/RAG · Learning · Reliability · Tools · Monitoring     │
├──────────────────────────────────────────────────────────────────────────────┤
│                             DOMAIN LAYER                                      │
│  Incident entity · IncidentQuery · Page[T] · Repository ABC                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 The Autonomous Core

### 1. AIOps Lifecycle Orchestrator

The `IncidentLifecycleOrchestrator` drives every incident through a state machine:

```
INGESTED ──▶ ANALYZED ──▶ (plan) ──▶ (execute) ──▶ VERIFIED / FAILED
```

1. **Ingest** — raw alerts normalized (`NormalizedEvent`, severity aliasing).
2. **Analyze** — `AutonomousDecisionEngine` + YAML `RemediationPlaybookEngine` classify the event and pick a playbook.
3. **Decide** — `RiskBasedExecutor` gates tool actions by risk level (auto / approval / blocked).
4. **Execute** — 5 specialized agents (`IncidentAgent`, `RcaAgent`, `PlannerAgent`, `ExecutionAgent`, `VerificationAgent`) run the remediation.
5. **Verify** — output validation decides `VERIFIED` vs `FAILED`; rollback available.

### 2. Advanced Reasoning Pipeline

The `ReasoningOrchestrator` adds a decision-intelligence layer on top:

- **Confidence** — `DecisionConfidenceEngine` scores decisions and flags risk levels.
- **Explanation** — `DecisionExplainer` produces human-readable rationale.
- **Verification** — `SelfVerificationLayer` validates recommendations pre-execution (min confidence `0.70`).
- **Model selection** — `DynamicModelSelector` routes tasks to model tiers by complexity (flash ↔ pro).
- **History** — every reasoning record is persisted and queryable per incident.

### 3. Real-Time Operations Command Center

The `OperationsCommandCenter` facade ties everything to live streams:

| Component | Responsibility |
|---|---|
| `EventPublisher` | In-memory pub/sub, thread-safe async streams (SSE, 15s keep-alive) |
| `IncidentTimeline` | Per-incident event timeline |
| `ActivityFeed` | Active agents, current tasks, completed actions, failures |
| `ExecutionMonitor` | Running/completed/failed agent executions with durations |
| `OperationsDashboard` | Incident / AI / execution metrics aggregation |

---

## 🔌 API Surface

> **60+ REST endpoints** across 12 routers. Full reference: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

| Area | Base | Highlights |
|---|---|---|
| Incidents | `/incidents` | CRUD + AI analysis |
| AIOps | `/aiops` | alert ingest, decide, playbooks, lifecycle run |
| Reasoning | `/reasoning` | reason, confidence, explain, verify, model select |
| Reliability | `/reliability` | recovery, rollback, RCA, correlation, chaos |
| Governance | `/governance` | RBAC, audit, approval policy, privacy mask |
| Optimization | `/optimization` | feedback, evaluation, routing, cost |
| Command Center | `/operations` | SSE stream, dashboard, metrics, executions |
| Workflow | `/incidents/{id}/workflow` | agent pipeline execution |
| Observability | `/metrics` · `/ai/providers` | Prometheus + provider health |

---

## 📂 Repository Layout

```
backend/
├── app/
│   ├── api/                 # routers (v1 + feature routes)
│   ├── application/         # services, DTOs, agents, orchestrator, workflows
│   ├── core/                # config, exceptions, logging, middleware
│   ├── domain/              # entities, models, repository interfaces
│   └── infrastructure/      # ai, aiops, command_center, reasoning, reliability,
│                            # governance, knowledge, learning, tools, monitoring
└── tests/                   # 471 tests across 15+ suites
```

---

## 🧪 Testing

| Suite | Coverage |
|---|---|
| `aiops/` | ingestion, decision, lifecycle, playbooks, risk execution |
| `reasoning/` | orchestrator, confidence, explanation, verification, model selection |
| `command_center/` | events/SSE, timeline, dashboard, execution monitor, API |
| `reliability/` | recovery, rollback, RCA, dependency intelligence, chaos |
| `governance/` | RBAC, audit, approval policy, privacy, model governance |
| `knowledge/` | RAG, embeddings, vector repository, retrieval agent |
| `learning/` | feedback, evaluation, routing/prompt/cost optimizers |
| `tools/` | executor, registry, 8 concrete integrations |

```bash
cd backend
python -m pytest tests/ -q          # full suite
python -m pytest tests/reasoning/   # targeted suite
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- MongoDB Atlas (optional; in-memory repository enabled by default)
- Gemini / OpenRouter API keys (for AI features)

### Install & Run

```bash
# 1. Create environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements-current.txt

# 3. Configure environment
cp .env.example .env      # add API keys, set REPOSITORY_TYPE=mongo

# 4. Start the server
cd backend
uvicorn app.main:app --reload
```

### Verify

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","version":"0.1.0",...}

open http://127.0.0.1:8000/docs        # interactive Swagger UI
```

---

## 🗺️ Roadmap

| Phase | Focus | Status |
|---|---|---|
| 1–17 | Foundation, incidents, AI gateway, AIOps, agents, tools, governance, knowledge, learning | ✅ Done |
| 18 | Reliability & resilience suite | ✅ Done |
| 19 | Advanced AI reasoning pipeline | ✅ Done |
| 20 | Real-time operations command center | ✅ Done |
| 21+ | Caching, distributed tracing, google-adk bridge, provider management | 🔜 Next |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web framework | FastAPI 0.140 + Uvicorn |
| AI SDKs | Google ADK, google-genai |
| LLM providers | Gemini, OpenRouter |
| Databases | MongoDB Atlas (Motor/PyMongo), in-memory fallback |
| Observability | Prometheus, structlog, OpenTelemetry |
| Quality | pytest, pytest-asyncio, ruff, black, mypy, pre-commit |

---

## 📄 Documentation

| Document | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Deep-dive architecture guide |
| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | Full endpoint reference |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Phased roadmap & progress |
| [`CURRENT_STATE.md`](CURRENT_STATE.md) | Live project status |
| [`NEXT_TASKS.md`](NEXT_TASKS.md) | Immediate next steps |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |

---

<div align="center">

**OpenOps AI** · Autonomous · Reliable · Governed · Observable

*Built with ⚡ in the open.*

</div>
