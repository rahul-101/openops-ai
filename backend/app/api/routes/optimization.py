from fastapi import APIRouter, Depends

from app.infrastructure.dependencies import (
    get_agent_analytics,
    get_cost_optimizer,
    get_evaluation_engine,
    get_feedback_engine,
    get_prompt_optimizer,
    get_routing_optimizer,
)
from app.infrastructure.learning.agent_analytics import (
    AgentAnalytics,
)
from app.infrastructure.learning.cost_optimizer import (
    CostOptimizer,
)
from app.infrastructure.learning.evaluation_engine import (
    EvaluationEngine,
)
from app.infrastructure.learning.feedback_engine import (
    FeedbackEngine,
)
from app.infrastructure.learning.prompt_optimizer import (
    PromptOptimizer,
)
from app.infrastructure.learning.routing_optimizer import (
    RoutingOptimizer,
)

router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"],
)


# ==========================================================
# Feedback Engine
# ==========================================================


@router.post(
    "/feedback/outcome",
    summary="Record AI recommendation outcome",
)
def record_outcome(
    body: dict,
    feedback: FeedbackEngine = Depends(get_feedback_engine),
):

    entry = feedback.record_outcome(
        recommendation_id=body.get("recommendation_id"),
        outcome=body.get("outcome"),
        incident_id=body.get("incident_id"),
        agent=body.get("agent"),
        model=body.get("model"),
        metadata=body.get("metadata") or {},
    )

    return {
        "id": entry.id,
        "recommendation_id": entry.recommendation_id,
        "outcome": entry.outcome,
    }


@router.post(
    "/feedback/human",
    summary="Record human feedback",
)
def record_human_feedback(
    body: dict,
    feedback: FeedbackEngine = Depends(get_feedback_engine),
):

    entry = feedback.record_human_feedback(
        recommendation_id=body.get("recommendation_id"),
        feedback=body.get("feedback"),
        outcome=body.get("outcome"),
    )

    return {
        "id": entry.id,
        "recommendation_id": entry.recommendation_id,
        "human_feedback": entry.human_feedback,
    }


@router.get(
    "/feedback/stats",
    summary="Feedback engine statistics",
)
def feedback_stats(
    feedback: FeedbackEngine = Depends(get_feedback_engine),
):

    return feedback.get_stats()


# ==========================================================
# AI Evaluation Engine
# ==========================================================


@router.post(
    "/evaluations",
    summary="Record an AI evaluation",
)
def record_evaluation(
    body: dict,
    evaluation: EvaluationEngine = Depends(get_evaluation_engine),
):

    record = evaluation.record_evaluation(
        incident_id=body.get("incident_id"),
        rca_accurate=body.get("rca_accurate", False),
        remediation_success=body.get(
            "remediation_success",
            False,
        ),
        resolution_time_ms=body.get("resolution_time_ms", 0),
        confidence=body.get("confidence", 0.0),
    )

    return {
        "id": record.id,
        "incident_id": record.incident_id,
        "outcome": record.outcome,
    }


@router.get(
    "/evaluations/stats",
    summary="AI evaluation engine statistics",
)
def evaluation_stats(
    evaluation: EvaluationEngine = Depends(get_evaluation_engine),
):

    return evaluation.get_stats()


# ==========================================================
# Routing Optimizer
# ==========================================================


@router.get(
    "/routing/rank",
    summary="Rank providers by learned performance",
)
def rank_providers(
    optimizer: RoutingOptimizer = Depends(get_routing_optimizer),
):

    return {
        "ranked_providers": optimizer.rank_providers(),
    }


@router.get(
    "/routing/performance",
    summary="Learned provider performance",
)
def provider_performance(
    optimizer: RoutingOptimizer = Depends(get_routing_optimizer),
):

    return [
        {
            "provider": p.provider,
            "total_calls": p.total_calls,
            "success_rate": p.success_rate,
            "average_latency_ms": p.average_latency_ms,
        }
        for p in optimizer.get_all_performance()
    ]


# ==========================================================
# Prompt Optimizer
# ==========================================================


@router.get(
    "/prompts/{prompt_name}/best",
    summary="Best performing prompt version",
)
def best_prompt(
    prompt_name: str,
    optimizer: PromptOptimizer = Depends(get_prompt_optimizer),
):

    return {
        "prompt_name": prompt_name,
        "best_version": optimizer.get_best_version(prompt_name),
    }


@router.get(
    "/prompts/{prompt_name}/versions",
    summary="Prompt version performance",
)
def prompt_versions(
    prompt_name: str,
    optimizer: PromptOptimizer = Depends(get_prompt_optimizer),
):

    return [
        {
            "version": p.version,
            "success_rate": p.success_rate,
            "average_latency_ms": p.average_latency_ms,
            "total_evaluations": p.total_evaluations,
        }
        for p in optimizer.list_versions(prompt_name)
    ]


# ==========================================================
# Agent Analytics
# ==========================================================


@router.get(
    "/agents",
    summary="Agent analytics",
)
def agent_analytics(
    agent: str | None = None,
    analytics: AgentAnalytics = Depends(get_agent_analytics),
):

    return [
        {
            "agent": stats.agent,
            "total_runs": stats.total_runs,
            "success_rate": stats.success_rate,
            "failed_runs": stats.failed_runs,
            "average_latency_ms": stats.average_latency_ms,
        }
        for stats in analytics.get_analytics(agent=agent)
    ]


@router.get(
    "/agents/summary",
    summary="Agent analytics summary",
)
def agent_summary(
    analytics: AgentAnalytics = Depends(get_agent_analytics),
):

    return analytics.get_summary()


# ==========================================================
# Cost Optimizer
# ==========================================================


@router.get(
    "/cost/choose",
    summary="Choose cheapest capable model",
)
def choose_model(
    input_tokens: int = 0,
    output_tokens: int = 0,
    optimizer: CostOptimizer = Depends(get_cost_optimizer),
):

    model = optimizer.choose(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    if model is None:
        return {"model": None}

    return {
        "provider": model.provider,
        "model": model.model,
        "estimated_cost_usd": model.estimated_cost(
            input_tokens,
            output_tokens,
        ),
    }
