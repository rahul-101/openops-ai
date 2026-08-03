"""
Populates realistic demo data on application startup.

Runs the real ingestion/lifecycle pipeline (so events, lifecycle
records, operations events and pending approvals are produced
authentically) and seeds the derived analytics stores that are
otherwise only populated by live AI calls.
"""

from app.core.logging import logger
from app.infrastructure.aiops.event_ingestion import RawAlert
from app.infrastructure.dependencies import (
    get_agent_analytics,
    get_incident_lifecycle_orchestrator,
    get_knowledge_base_service,
    get_model_governance_service,
)

DEMO_ALERTS = [
    {
        "source": "kubernetes",
        "alert_id": "demo-pod-crash",
        "title": "Pod crash loop detected",
        "description": (
            "payments-api pod has entered CrashLoopBackOff after 3 "
            "restarts within 5 minutes. Restarting the deployment "
            "requires operator approval."
        ),
        "severity": "medium",
        "service": "payments",
        "tags": ["crash", "restart"],
    },
    {
        "source": "kubernetes",
        "alert_id": "demo-memory",
        "title": "Memory pressure on worker node",
        "description": (
            "worker-pool node reporting high memory pressure; pods at "
            "risk of OOMKill. Remediation requires operator approval."
        ),
        "severity": "high",
        "service": "workers",
        "tags": ["memory"],
    },
    {
        "source": "kubernetes",
        "alert_id": "demo-health",
        "title": "Payments API health check degraded",
        "description": (
            "Health probe latency elevated on payments-api. Running "
            "low-risk diagnostics and logging a ServiceNow incident."
        ),
        "severity": "low",
        "service": "payments",
        "tags": ["health", "status"],
    },
]

AGENT_RUNS = {
    "incident": {"runs": 24, "success": 23, "latency_ms": 340.0},
    "rca": {"runs": 24, "success": 22, "latency_ms": 680.0},
    "planner": {"runs": 24, "success": 21, "latency_ms": 190.0},
    "execution": {"runs": 24, "success": 22, "latency_ms": 420.0},
    "verification": {"runs": 24, "success": 24, "latency_ms": 260.0},
}

MODEL_USAGE = [
    ("gemini", "gemini-2.0-flash", 1840, 620, 0.024, 410.0, "reasoning"),
    ("gemini", "gemini-2.0-flash", 1240, 380, 0.017, 385.0, "incident_analysis"),
    ("gemini", "gemini-2.0-flash", 960, 240, 0.012, 360.0, "chat"),
    ("openrouter", "openrouter/free", 2100, 740, 0.0, 780.0, "reasoning"),
    ("openrouter", "openrouter/free", 1480, 460, 0.0, 720.0, "incident_analysis"),
]

KNOWLEDGE_DOCS = [
    {
        "title": "Kubernetes CrashLoopBackOff recovery",
        "content": (
            "1. Check pod status and restart count. "
            "2. Inspect container logs for the crash reason. "
            "3. Verify resource limits; a restart is approved only "
            "for verified transient faults. "
            "4. After restart, confirm readiness and re-run health checks."
        ),
        "type": "runbook",
    },
    {
        "title": "Payments API latency incident — resolution",
        "content": (
            "Elevated latency on payments-api traced to connection "
            "pool exhaustion during a traffic spike. Mitigated by "
            "scaling the deployment and warming the connection pool. "
            "Permanent fix tracks raising pool max connections."
        ),
        "type": "resolution",
    },
]


async def seed_demo_data() -> None:
    """
    Seeds demo data by replaying the real pipeline and derived stores.
    """

    orchestrator = get_incident_lifecycle_orchestrator()

    for spec in DEMO_ALERTS:

        alert = RawAlert(**spec)

        incident = await orchestrator.handle_alert(alert)

        logger.info(
            "Seeded lifecycle",
            incident_id=incident.incident_id,
            status=incident.status.value,
            playbook=next(
                (s.details.get("playbook") for s in incident.steps if s.stage == "remediation"),
                None,
            ),
        )

    analytics = get_agent_analytics()

    for agent, stats in AGENT_RUNS.items():

        for _ in range(stats["runs"]):

            analytics.record_run(
                agent=agent,
                success=(
                    _ < stats["success"]
                ),
                latency_ms=stats["latency_ms"],
            )

    governance = get_model_governance_service()

    for provider, model, input_tokens, output_tokens, cost, latency, action in MODEL_USAGE:

        governance.record_usage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
            action=action,
        )

    knowledge = get_knowledge_base_service()

    for doc in KNOWLEDGE_DOCS:

        if doc["type"] == "runbook":

            knowledge.store_runbook(
                title=doc["title"],
                content=doc["content"],
            )

        else:

            knowledge.store_resolution(
                title=doc["title"],
                content=doc["content"],
            )

    logger.info("Demo data seeding complete")
