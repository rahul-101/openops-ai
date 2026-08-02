<div align="center">

<h1 style="font-size:42px;margin:32px 0 8px;background:linear-gradient(90deg,#00ff9c,#a855f7);-webkit-background-clip:text;background-clip:text;color:transparent">🧪 TESTING</h1>
<p style="color:#8b93b0;letter-spacing:3px;text-transform:uppercase;font-size:13px">Quality Guide</p>

</div>

---

# 🧪 OpenOps AI — Testing Guide

> **471 tests passing** · 70 test files · 15+ suites · ~10,700 lines of test code.

---

## 🚀 Quick Start

```bash
cd backend

# Full suite
python -m pytest tests/ -q

# Single suite
python -m pytest tests/reasoning/ -q

# Single test
python -m pytest tests/command_center/test_events.py::TestEventPublisher -q

# With coverage
python -m pytest tests/ -q --cov=app
```

---

## 🗂️ Test Suites

| Suite | Modules Under Test | Key Coverage |
|---|---|---|
| `tests/aiops/` | ingestion, decision, lifecycle, playbooks, risk | normalization, severity aliasing, state machine, risk gating |
| `tests/reasoning/` | orchestrator, confidence, explanation, verification, history, model selection | multi-agent reasoning, confidence/risk, self-verification |
| `tests/command_center/` | events, timeline, dashboard, execution monitor, API | pub/sub, SSE streaming, aggregates, endpoints |
| `tests/reliability/` | recovery, rollback, RCA, dependency intelligence, correlation, chaos | checkpoint/resume, rollback, impact scoring |
| `tests/governance/` | RBAC, audit, approval policy, privacy, model governance, prompt registry | permissions, PII masking, risk policies |
| `tests/knowledge/` | ingestion, embeddings, vector repository, memory, retrieval | RAG pipeline, cosine similarity, retrieval ranking |
| `tests/learning/` | feedback, evaluation, routing/prompt/cost optimizers, analytics | outcome learning, provider ranking, cost selection |
| `tests/tools/` | executor, registry, 8 integrations | action execution, approval gating, transport |
| `tests/ai/` | router, health, metrics, scorer, routing | circuit breaker, failover, provider scoring |
| `tests/workflows/` | engine, incident workflow | agent pipeline, checkpoint, status transitions |
| `tests/agents/` | registry, orchestrator | agent lifecycle |
| `tests/domain/` · `services/` | incident entity, service | CRUD, pagination |

---

## ⚙️ Conventions

### Async Tests

Async tests require the `@pytest.mark.asyncio` marker:

```python
import pytest

@pytest.mark.asyncio
async def test_stream_receives_event():
    stream = publisher.open_stream()
    publisher.publish(event)
    payload = await asyncio.wait_for(stream.get(), timeout=1.0)
    assert payload["incident_id"] == event.incident_id
```

### Fixtures

`tests/conftest.py` inserts the backend directory into `sys.path` so tests import via `app.*`:

```python
from app.infrastructure.command_center.events import EventPublisher
```

### SSE Streaming Tests

`TestClient` buffers full responses, so infinite SSE streams are tested by invoking the endpoint and consuming its `body_iterator` directly:

```python
response = await stream_events(center)
generator = response.body_iterator
chunk = await asyncio.wait_for(anext(generator), timeout=3.0)
```

---

## 🧠 Testing Real-Time & Multi-Agent Systems

| Challenge | Approach |
|---|---|
| Thread safety | In-memory stores use `threading.Lock`; tests verify concurrent fan-out |
| Cross-thread SSE | Publisher uses `loop.call_soon_threadsafe` for queue delivery |
| Determinism | Use `pytest.approx` for float aggregates; inject stub services (e.g. `StubIncidentService`) |
| Async determinism | `asyncio.wait_for(..., timeout=)` wraps every async assertion |

---

## 🔍 Lint & Types

```bash
ruff check backend/app backend/tests    # lint (line-length 88)
mypy backend/app                        # static types (Python 3.11+)
black --check backend/app               # formatting
```

---

<div align="center">
<strong style="color:#00ff9c">471/471 green</strong> · <span style="color:#8b93b0">Quality is a feature, not an afterthought</span>
</div>
