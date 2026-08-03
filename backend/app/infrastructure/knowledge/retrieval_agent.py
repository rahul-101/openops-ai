from app.application.agents.agent import Agent
from app.application.agents.agent_context import AgentContext
from app.application.agents.agent_metadata import AgentMetadata
from app.application.agents.agent_result import (
    AgentResult,
    AgentStatus,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)


class KnowledgeRetrievalAgent(Agent):
    """
    Retrieves similar incidents and previous solutions from
    the knowledge base and provides them as context to
    workflow agents.
    """

    def __init__(
        self,
        knowledge_base: KnowledgeBaseService,
        limit: int = 3,
    ) -> None:

        super().__init__(
            AgentMetadata(
                name="knowledge_retrieval",
                description=(
                    "Searches similar incidents and previous "
                    "solutions from the knowledge base."
                ),
                order=0,
            )
        )

        self.knowledge_base = knowledge_base
        self.limit = limit

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:

        title = context.input.get("title", "")

        description = context.input.get("description", "")

        try:

            results = self.knowledge_base.search(
                query=f"{title} {description}",
                limit=self.limit,
            )

        except Exception as ex:

            return AgentResult(
                agent=self.name,
                status=AgentStatus.FAILURE,
                error=str(ex),
            )

        matches = [
            {
                "id": result.document_id,
                "title": result.title,
                "content": result.content,
                "type": result.type,
                "score": result.score,
            }
            for result in results
        ]

        context.set(
            "knowledge_context",
            matches,
        )

        for result in results[:2]:
            context.add_recommendation(
                f"Reference {result.type}: {result.title}"
            )

        return AgentResult(
            agent=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "matches": len(matches),
                "similar": matches,
            },
        )
