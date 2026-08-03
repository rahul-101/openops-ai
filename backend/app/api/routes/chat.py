import re

from fastapi import APIRouter, Depends

from app.infrastructure.aiops.event_ingestion import (
    EventIngestionEngine,
)
from app.infrastructure.aiops.lifecycle import (
    IncidentLifecycleOrchestrator,
)
from app.infrastructure.aiops.playbook_engine import (
    RemediationPlaybookEngine,
)
from app.infrastructure.aiops.risk_based_execution import (
    RiskBasedExecutor,
)
from app.infrastructure.dependencies import (
    get_approval_workflow,
    get_event_ingestion_engine,
    get_incident_lifecycle_orchestrator,
    get_playbook_engine,
    get_reasoning_orchestrator,
    get_risk_based_executor,
)
from app.infrastructure.reasoning.orchestrator import (
    ReasoningOrchestrator,
)
from app.infrastructure.tools.approval import ApprovalWorkflow

router = APIRouter(
    prefix="/chat",
    tags=["AI Chat"],
)

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


@router.post(
    "",
    summary="Answer a natural-language question grounded in platform data",
)
async def chat(
    body: dict,
    ingestion: EventIngestionEngine = Depends(
        get_event_ingestion_engine,
    ),
    orchestrator: ReasoningOrchestrator = Depends(
        get_reasoning_orchestrator,
    ),
    lifecycle: IncidentLifecycleOrchestrator = Depends(
        get_incident_lifecycle_orchestrator,
    ),
    playbooks: RemediationPlaybookEngine = Depends(
        get_playbook_engine,
    ),
    risk: RiskBasedExecutor = Depends(get_risk_based_executor),
    approval_workflow: ApprovalWorkflow = Depends(
        get_approval_workflow,
    ),
):

    message = (body.get("message") or "").strip()

    if not message:
        return {"reply": "Ask me anything about your operations."}

    event_id = body.get("event_id")

    if not event_id:
        event_id = _find_event_reference(message, ingestion)

    if event_id is not None:
        report = await _reason_on_event(
            event_id,
            ingestion,
            orchestrator,
        )
        if report is not None:
            return {"reply": _format_report(report)}

    return {
        "reply": _format_summary(
            message,
            lifecycle,
            playbooks,
            risk,
            approval_workflow,
        )
    }


# ==========================================================
# Helpers
# ==========================================================


def _find_event_reference(
    message: str,
    ingestion: EventIngestionEngine,
) -> str | None:

    match = _UUID_RE.search(message)

    if match:
        candidate = match.group(0)
        if ingestion.get(candidate) is not None:
            return candidate

    for event in ingestion.list(limit=50):
        tokens = [
            token
            for token in (
                event.title,
                event.source,
                event.service,
            )
            if token
        ]
        haystack = " ".join(tokens).lower()
        if any(
            word in message.lower()
            for word in haystack.split()
            if len(word) > 3
        ):
            return event.event_id

    return None


async def _reason_on_event(
    event_id: str,
    ingestion: EventIngestionEngine,
    orchestrator: ReasoningOrchestrator,
):

    event = ingestion.get(event_id)

    if event is None:
        return None

    return await orchestrator.reason(event)


def _format_report(report) -> str:

    lines = [
        "## Reasoning report",
        "",
        f"**Incident** `{report.incident_id[:8]}`",
        f"- **Decision:** `{report.decision}`",
        f"- **Confidence:** `{report.confidence:.0%}`",
        f"- **Risk:** `{report.risk}`",
        f"- **Validated:** `{'yes' if report.validated else 'no'}`",
        "",
        "### Reasoning chain",
    ]

    if report.reasoning:
        lines.extend(f"- {line}" for line in report.reasoning)
    else:
        lines.append("- no reasoning steps recorded")

    if report.evidence:
        lines.append("")
        lines.append("### Evidence")
        lines.extend(f"- {line}" for line in report.evidence)

    if report.alternatives:
        lines.append("")
        lines.append("### Alternatives considered")
        lines.extend(f"- {line}" for line in report.alternatives)

    if report.agents_involved:
        lines.append("")
        lines.append(
            "### Agents involved: "
            + ", ".join(f"`{agent}`" for agent in report.agents_involved)
        )

    return "\n".join(lines)


def _format_summary(
    message: str,
    lifecycle,
    playbooks,
    risk,
    approval_workflow,
) -> str:

    records = lifecycle.list()
    playbook_list = playbooks.list()
    risk_actions = risk.actions()
    pending = approval_workflow.list_pending()

    running = [
        r for r in records if r.status.value in ("running", "in_progress")
    ]
    completed = [r for r in records if r.status.value == "completed"]

    lines = [
        "## Operations summary",
        "",
        f"Here's what I found in your workspace for **\"{message}\"**:",
        "",
        "### Live state",
        f"- **Lifecycle records:** `{len(records)}` total "
        f"(`{len(running)}` running, `{len(completed)}` completed)",
        f"- **Remediation playbooks:** `{len(playbook_list)}` registered",
        f"- **Risk-gated actions:** `{len(risk_actions)}` tracked",
        f"- **Pending approvals:** `{len(pending)}`",
        "",
    ]

    if pending:
        lines.append("### Awaiting your approval")
        for approval in pending:
            lines.append(
                f"- `{approval.tool_name}.{approval.parameters.get('action')}` "
                f"(`{approval.id[:8]}`)"
            )
        lines.append("")

    if playbook_list:
        lines.append("### Playbooks")
        for playbook in playbook_list:
            lines.append(
                f"- **{playbook.name}** — {playbook.description} "
                f"({len(playbook.steps)} steps)"
            )
        lines.append("")

    if records:
        lines.append("### Recent lifecycle runs")
        for record in list(reversed(records))[:5]:
            lines.append(
                f"- `{record.incident_id[:8]}` → "
                f"`{record.status.value}` "
                f"(servicenow: {'yes' if record.servicenow_updated else 'no'})"
            )

    lines.append("")
    lines.append(
        "> You can also ask me about a specific event by mentioning its "
        "title, source, or incident id — I'll run the reasoning pipeline on it."
    )

    return "\n".join(lines)
