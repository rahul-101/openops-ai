<div align="center">

<h1 style="font-size:42px;margin:32px 0 8px;background:linear-gradient(90deg,#ff2ec4,#00e5ff);-webkit-background-clip:text;background-clip:text;color:transparent">📡 API REFERENCE</h1>
<p style="color:#8b93b0;letter-spacing:3px;text-transform:uppercase;font-size:13px">60+ Endpoints · 12 Routers</p>

</div>

---

# 📡 OpenOps AI — API Reference

> Interactive docs available at **`/docs`** (Swagger UI) when the server runs. Base URL: `http://127.0.0.1:8000`.

---

## 🟢 Health & Root

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Liveness check (service + version) |
| `GET` | `/demo-error` | Demo of 404 error handler |

---

## 🗂️ Incidents

| Method | Path | Description |
|---|---|---|
| `POST` | `/incidents` | Create incident → **201** |
| `GET` | `/incidents` | List (page, size, status, severity, source, search, sort_by, order) |
| `GET` | `/incidents/{incident_id}` | Get by ID |
| `PUT` | `/incidents/{incident_id}` | Update incident |
| `DELETE` | `/incidents/{incident_id}` | Delete → **204** |
| `POST` | `/incidents/analyze` | AI analysis of an incident (Gemini via router) |

---

## 🤖 AIOps

| Method | Path | Description |
|---|---|---|
| `POST` | `/aiops/alerts/ingest` | Ingest raw alert → `NormalizedEvent` |
| `GET` | `/aiops/events` | List normalized events (source, limit) |
| `POST` | `/aiops/decide` | Analyze event + select remediation |
| `GET` | `/aiops/risk/actions` | List registered risk actions |
| `GET` | `/aiops/playbooks` | List remediation playbooks |
| `POST` | `/aiops/lifecycle/run` | Run end-to-end incident lifecycle |
| `GET` | `/aiops/lifecycle/{incident_id}` | Get lifecycle record |
| `GET` | `/aiops/lifecycle` | List lifecycle records |

---

## 🧠 Reasoning

| Method | Path | Description |
|---|---|---|
| `POST` | `/reasoning/reason` | Multi-agent reasoning for an incident |
| `POST` | `/reasoning/confidence` | Evaluate decision confidence + risk |
| `POST` | `/reasoning/explain` | Explain an autonomous decision |
| `POST` | `/reasoning/verify` | Validate recommendation pre-execution |
| `POST` | `/reasoning/model/select` | Select model by task complexity |
| `GET` | `/reasoning/model/classify` | Classify task complexity |
| `GET` | `/reasoning/model/models` | List registered model tiers |
| `GET` | `/reasoning/history` | List reasoning history |
| `GET` | `/reasoning/history/{incident_id}` | Reasoning history for an incident |

---

## ♻️ Reliability

| Method | Path | Description |
|---|---|---|
| `POST` | `/reliability/workflows/begin` | Begin recoverable workflow |
| `POST` | `/reliability/workflows/{workflow_id}/checkpoint` | Checkpoint completed step |
| `GET` | `/reliability/workflows/{workflow_id}/resume` | Remaining steps |
| `POST` | `/reliability/rollback/begin` | Begin rollback record |
| `POST` | `/reliability/rca/{incident_id}/factors` | Add root cause factor |
| `GET` | `/reliability/rca/{incident_id}/ranked` | Rank root causes |
| `POST` | `/reliability/dependencies` | Register service dependency |
| `GET` | `/reliability/dependencies/{service}/impact` | Impact analysis |
| `POST` | `/reliability/correlate` | Duplicate/relation check |
| `POST` | `/reliability/impact/analyze` | Business impact calculation |
| `POST` | `/reliability/chaos/inject` | Inject simulated failure |
| `POST` | `/reliability/chaos/{experiment_id}/validate` | Validate autonomous recovery |
| `GET` | `/reliability/chaos/recovery-rate` | Autonomous recovery rate |

---

## 🏛️ Governance

| Method | Path | Description |
|---|---|---|
| `POST` | `/governance/rbac/check` | Check user permission |
| `GET` | `/governance/audit` | Query audit log (user, action, incident_id, decision, limit) |
| `GET` | `/governance/approval-policy/actions` | List actions + risk levels |
| `GET` | `/governance/approval-policy/{action}/decision` | Evaluate action against policy |
| `GET` | `/governance/prompts/{name}` | Get active prompt version |
| `GET` | `/governance/models/stats` | Model usage/cost stats |
| `POST` | `/governance/privacy/mask` | Detect + mask sensitive data |

---

## 📈 Optimization

| Method | Path | Description |
|---|---|---|
| `POST` | `/optimization/feedback/outcome` | Record AI recommendation outcome |
| `POST` | `/optimization/feedback/human` | Record human feedback |
| `GET` | `/optimization/feedback/stats` | Feedback engine statistics |
| `POST` | `/optimization/evaluations` | Record AI evaluation |
| `GET` | `/optimization/evaluations/stats` | Evaluation engine statistics |
| `GET` | `/optimization/routing/rank` | Rank providers by learned performance |
| `GET` | `/optimization/routing/performance` | Learned provider performance |
| `GET` | `/optimization/prompts/{prompt_name}/best` | Best performing prompt version |
| `GET` | `/optimization/prompts/{prompt_name}/versions` | Prompt version performance |
| `GET` | `/optimization/agents` | Agent analytics |
| `GET` | `/optimization/agents/summary` | Agent analytics summary |
| `GET` | `/optimization/cost/choose` | Choose cheapest capable model |

---

## ⚡ Operations Command Center

| Method | Path | Description |
|---|---|---|
| `GET` | `/operations/events/stream` | **SSE** real-time event stream (15s keep-alive) |
| `GET` | `/operations/events` | Recent events (limit 1–500, event_type, incident_id) |
| `GET` | `/incidents/{incident_id}/timeline` | Incident timeline |
| `GET` | `/ai/activity` | AI activity feed snapshot |
| `GET` | `/operations/executions` | Tracked executions + summary |
| `GET` | `/operations/executions/{execution_id}` | Single execution |
| `GET` | `/operations/dashboard` | Full dashboard snapshot |
| `GET` | `/operations/metrics/incidents` | Incident metrics |
| `GET` | `/operations/metrics/ai` | AI metrics |
| `GET` | `/operations/metrics/execution` | Execution metrics |

### SSE Payload Example

```json
data: {
  "event_id": "b064dc6d-bb75-4870-a0f7-53357d11a515",
  "type": "analysis_started",
  "category": "agent",
  "incident_id": "inc-1",
  "agent": "reasoning",
  "action": "analyze",
  "status": "",
  "duration_ms": 0.0,
  "metadata": {},
  "timestamp": "2026-08-02T13:01:19.146771"
}
```

### Event Types

| Type | Category |
|---|---|
| `incident_created` · `incident_resolved` | incident |
| `analysis_started` · `rca_completed` · `decision_created` | agent |
| `tool_execution_started` · `tool_execution_completed` | execution |

---

## 🔀 Workflow

| Method | Path | Description |
|---|---|---|
| `POST` | `/incidents/{incident_id}/workflow/run` | Execute agent pipeline (triage → analysis → recommendation) |

---

## 📊 Observability

| Method | Path | Description |
|---|---|---|
| `GET` | `/metrics` | Prometheus exposition (`text/plain; version=0.0.4`) |
| `GET` | `/ai/providers/health` | Provider health / circuit states |
| `GET` | `/ai/providers/metrics` | Provider metrics |

---

<div align="center">
<strong style="color:#00ff9c">Full interactive reference: http://127.0.0.1:8000/docs</strong>
</div>
