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
tr:nth-child(even){background:#0a0e1f}
blockquote{border-left:3px solid var(--cyan);background:#0b0f1e;padding:8px 16px;color:var(--muted)}
hr{border:none;height:1px;background:linear-gradient(90deg,var(--cyan),var(--magenta),transparent)}
</style>

<h1 style="font-size:42px;margin:32px 0 8px;background:linear-gradient(90deg,#ffb86c,#ff2ec4);-webkit-background-clip:text;background-clip:text;color:transparent">🤝 CONTRIBUTING</h1>
<p style="color:#8b93b0;letter-spacing:3px;text-transform:uppercase;font-size:13px">How to Contribute</p>

</div>

---

# 🤝 Contributing to OpenOps AI

> Thanks for helping build the autonomous incident response platform! Every contribution counts.

---

## ✨ Getting Started

1. **Fork** the repository.
2. **Clone** your fork:

   ```bash
   git clone https://github.com/your-user/openops-ai.git
   cd openops-ai
   ```

3. **Set up the environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-current.txt
   cp .env.example .env
   ```

4. **Create a branch**:

   ```bash
   git checkout -b feat/your-feature
   ```

---

## 🧑‍💻 Development Loop

```bash
# Backend
cd backend
uvicorn app.main:app --reload      # dev server on :8000

# Tests
python -m pytest tests/ -q

# Lint / type / format
ruff check app tests
mypy app
black app tests
```

---

## 📝 Code Style

- Python **3.11+**, `line-length = 88`.
- **Black** formatting · **Ruff** linting · **mypy** strict typing.
- Follow the **layered architecture** (`api → application → domain → infrastructure`).
- New features need **DI providers** in `app/infrastructure/dependencies.py`.
- New routers register in `app/api/router.py`.
- **No new tests → no merge.** Every phase ships with a green suite.

### Naming & Structure

| Layer | Convention | Example |
|---|---|---|
| Router | `app/api/routes/<area>.py` | `routes/reasoning.py` |
| Service | `app/application/services/<name>_service.py` | `incident_service.py` |
| Domain | `app/domain/entities/<name>.py` | `incident.py` |
| Infra | `app/infrastructure/<area>/` | `infrastructure/reasoning/` |
| Tests | `tests/<area>/test_<module>.py` | `tests/reasoning/test_confidence.py` |

---

## 🧪 Writing Tests

1. Place tests under `tests/<area>/`.
2. Import via `app.*` (conftest adds the backend to `sys.path`).
3. Mark async tests with `@pytest.mark.asyncio`.
4. Stub external dependencies (DB, LLM, HTTP) — never hit real services.
5. Run the **full suite** before opening a PR.

```python
# tests/reasoning/test_confidence.py
from app.infrastructure.reasoning.confidence import DecisionConfidenceEngine

def test_low_risk_decision_is_safe():
    engine = DecisionConfidenceEngine()
    result = engine.evaluate(decision="restart", risk="low")
    assert result.validated is True
```

---

## 🔀 Pull Request Checklist

- [ ] Feature branch off `main`
- [ ] Code formatted with **black**
- [ ] Lint clean with **ruff**
- [ ] Types check with **mypy**
- [ ] New tests added & **passing**
- [ ] Full suite **green** (`python -m pytest tests/ -q`)
- [ ] `CHANGELOG.md` updated
- [ ] Docs updated (`docs/`, `README.md` if API changes)

---

## 🗺️ Where to Start

Unsure where to dive in? Try the **[ROADMAP](ROADMAP.md)**:

- 🔄 **Phase 21 (Cache)** — implement `RedisCache`, `SemanticCache`, `PromptCache`.
- 🔄 **Phase 22 (Tracing)** — build `Tracer` + `SpanBuilder` on OpenTelemetry.
- 🔄 **Phase 23 (ADK)** — wire the google-adk bridge.
- 🔜 **Phase 25 (Frontend)** — React command center UI on the SSE stream.

---

<div align="center">
<strong style="color:#00ff9c">Open source, open ops.</strong><br>
<span style="color:#8b93b0">Questions? Open an issue or start a discussion.</span>
</div>
