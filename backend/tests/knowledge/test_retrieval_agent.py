import pytest

from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_result import AgentStatus
from app.infrastructure.knowledge.embedding_service import (
    HashingEmbeddingService,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.retrieval_agent import (
    KnowledgeRetrievalAgent,
)
from app.infrastructure.knowledge.vector.in_memory_vector_repository import (
    InMemoryVectorRepository,
)


@pytest.fixture
def knowledge_base() -> KnowledgeBaseService:

    knowledge_base = KnowledgeBaseService(
        repository=InMemoryVectorRepository(),
        embedding_service=HashingEmbeddingService(),
    )

    knowledge_base.store_resolution(
        title="Pool resize",
        content="increase the database connection pool size",
        metadata={"category": "database"},
    )

    knowledge_base.store_incident(
        title="DB timeout",
        description="connection pool exhausted under load",
        category="database",
    )

    return knowledge_base


@pytest.mark.asyncio
async def test_retrieves_context(knowledge_base):

    agent = KnowledgeRetrievalAgent(knowledge_base)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
        input={
            "title": "Database timeout",
            "description": "connection pool exhausted",
        },
    )

    result = await agent.execute(context)

    assert result.status == AgentStatus.SUCCESS
    assert result.output["matches"] >= 1

    knowledge_context = context.get("knowledge_context")

    assert knowledge_context is not None
    assert len(knowledge_context) >= 1
    assert "content" in knowledge_context[0]

    assert any(
        "Reference" in recommendation
        for recommendation in context.recommendations
    )


@pytest.mark.asyncio
async def test_empty_knowledge_returns_no_matches():

    knowledge_base = KnowledgeBaseService(
        repository=InMemoryVectorRepository(),
        embedding_service=HashingEmbeddingService(),
    )

    agent = KnowledgeRetrievalAgent(knowledge_base)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
        input={
            "title": "Anything",
            "description": "nothing stored yet",
        },
    )

    result = await agent.execute(context)

    assert result.status == AgentStatus.SUCCESS
    assert result.output["matches"] == 0
    assert context.get("knowledge_context") == []


@pytest.mark.asyncio
async def test_provides_context_to_workflow_agents(knowledge_base):

    from app.application.agents.agent_registry import AgentRegistry
    from app.application.orchestration.agent_orchestrator import (
        AgentOrchestrator,
    )
    from app.infrastructure.ai.agents.recommendation_agent import (
        RecommendationAgent,
    )

    registry = AgentRegistry()

    registry.register(
        KnowledgeRetrievalAgent(knowledge_base)
    )

    registry.register(RecommendationAgent())

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        incident_id="inc-1",
        workflow_id="wf-1",
        input={
            "title": "Database timeout",
            "description": "connection pool exhausted",
        },
    )

    await orchestrator.run(context)

    assert context.get("knowledge_context") is not None

    final_recommendations = context.get(
        "final_recommendations",
        [],
    )

    assert len(final_recommendations) >= 1
