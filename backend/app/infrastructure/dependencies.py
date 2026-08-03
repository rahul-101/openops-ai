"""
Application dependency providers.
"""

from functools import lru_cache

from app.application.services.incident_analysis_service import (
    IncidentAnalysisService,
)
from app.application.services.incident_service import IncidentService
from app.core.config import settings
from app.domain.repositories.incident_repository import IncidentRepository

from app.infrastructure.ai.agents.incident_agent import IncidentAgent

from app.application.agents.agent_registry import AgentRegistry
from app.application.orchestration.agent_orchestrator import (
    AgentOrchestrator,
)
from app.application.workflows.incident_workflow import (
    IncidentWorkflow,
)
from app.application.workflows.workflow_engine import (
    WorkflowEngine,
)

from app.infrastructure.adk.adk_orchestrator import (
    AdkOrchestrator,
)

from app.infrastructure.knowledge.embedding_service import (
    EmbeddingService,
    HashingEmbeddingService,
)
from app.infrastructure.knowledge.document_ingestion import (
    DocumentIngestionPipeline,
)
from app.infrastructure.knowledge.incident_memory_repository import (
    IncidentMemoryRepository,
)
from app.infrastructure.knowledge.incident_memory_service import (
    IncidentMemoryService,
)
from app.infrastructure.knowledge.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.infrastructure.knowledge.retrieval_agent import (
    KnowledgeRetrievalAgent,
)
from app.infrastructure.knowledge.vector_repository import (
    VectorRepository,
)

from app.infrastructure.tools.approval import ApprovalWorkflow
from app.infrastructure.tools.executor import ToolExecutor
from app.infrastructure.tools.registry import ToolRegistry

from app.infrastructure.governance.approval_policy import (
    ApprovalPolicyEngine,
)
from app.infrastructure.governance.audit_log import (
    AuditLogService,
)
from app.infrastructure.governance.data_privacy import (
    DataPrivacyService,
)
from app.infrastructure.governance.model_governance import (
    ModelGovernanceService,
)
from app.infrastructure.governance.prompt_registry import (
    PromptRegistry,
)
from app.infrastructure.governance.rbac import RbacService
from app.infrastructure.governance.models import RiskLevel

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

from app.infrastructure.aiops.agents import (
    ExecutionAgent as AioOpsExecutionAgent,
)
from app.infrastructure.aiops.agents import (
    IncidentAgent as AioOpsIncidentAgent,
)
from app.infrastructure.aiops.agents import (
    MultiAgentRunner as AioOpsMultiAgentRunner,
)
from app.infrastructure.aiops.agents import (
    PlannerAgent as AioOpsPlannerAgent,
)
from app.infrastructure.aiops.agents import (
    RcaAgent as AioOpsRcaAgent,
)
from app.infrastructure.aiops.agents import (
    VerificationAgent as AioOpsVerificationAgent,
)
from app.infrastructure.aiops.decision_engine import (
    AutonomousDecisionEngine,
)
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

from app.infrastructure.reliability.business_impact import (
    BusinessImpactAnalysis,
)
from app.infrastructure.reliability.chaos_simulator import (
    ChaosTestingSimulator,
)
from app.infrastructure.reliability.dependency_intelligence import (
    DependencyIntelligence,
)
from app.infrastructure.reliability.incident_correlation import (
    IncidentCorrelation,
)
from app.infrastructure.reliability.rollback import (
    RemediationRollback,
)
from app.infrastructure.reliability.root_cause_graph import (
    RootCauseGraph,
)
from app.infrastructure.reliability.workflow_recovery import (
    WorkflowRecovery,
)

from app.infrastructure.reasoning.confidence import (
    DecisionConfidenceEngine,
)
from app.infrastructure.reasoning.explanation import (
    DecisionExplainer,
)
from app.infrastructure.reasoning.history import (
    ReasoningHistoryStore,
)
from app.infrastructure.reasoning.model_selection import (
    DynamicModelSelector,
)
from app.infrastructure.reasoning.multi_agent import (
    DecisionAgent as ReasoningDecisionAgent,
)
from app.infrastructure.reasoning.multi_agent import (
    IncidentAnalysisAgent as ReasoningIncidentAnalysisAgent,
)
from app.infrastructure.reasoning.multi_agent import (
    MultiAgentReasoningRunner,
)
from app.infrastructure.reasoning.multi_agent import (
    RcaAgent as ReasoningRcaAgent,
)
from app.infrastructure.reasoning.multi_agent import (
    VerificationAgent as ReasoningVerificationAgent,
)
from app.infrastructure.reasoning.orchestrator import (
    ReasoningOrchestrator,
)
from app.infrastructure.reasoning.verification import (
    SelfVerificationLayer,
)

from app.infrastructure.command_center.activity_feed import (
    ActivityFeed,
)
from app.infrastructure.command_center.command_center import (
    OperationsCommandCenter,
)
from app.infrastructure.command_center.dashboard import (
    OperationsDashboard,
)
from app.infrastructure.command_center.events import (
    EventPublisher,
)
from app.infrastructure.command_center.execution_monitor import (
    ExecutionMonitor,
)
from app.infrastructure.command_center.incident_timeline import (
    IncidentTimeline,
)

from app.infrastructure.cache.cache_key_builder import (
    CacheKeyBuilder,
)
from app.infrastructure.cache.cache_service import (
    CacheService,
    InMemoryCacheService,
)
from app.infrastructure.cache.prompt_cache import (
    PromptCache,
)
from app.infrastructure.cache.redis_cache import (
    RedisCacheService,
)
from app.infrastructure.cache.semantic_cache import (
    SemanticCache,
)

from app.infrastructure.tracing.tracer import (
    Tracer,
)

from app.infrastructure.ai.health.provider_health_service import (
    ProviderHealthService,
)

from app.infrastructure.ai.metrics.provider_metrics_service import (
    ProviderMetricsService,
)

from app.infrastructure.ai.providers.gemini_provider import (
    GeminiProvider,
)

from app.infrastructure.ai.providers.openrouter_provider import (
    OpenRouterProvider,
)

from app.infrastructure.ai.registry.provider_metadata import (
    ProviderCapability,
    ProviderMetadata,
)

from app.infrastructure.ai.registry.provider_metadata_registry import (
    ProviderMetadataRegistry,
)

from app.infrastructure.ai.registry.provider_registry import (
    ProviderRegistry,
)

from app.infrastructure.ai.bootstrap.provider_bootstrap import (
    ProviderBootstrap,
)

from app.infrastructure.ai.router.ai_router import (
    AIRouter,
)

from app.infrastructure.ai.routing.priority_routing_policy import (
    PriorityRoutingPolicy,
)

from app.infrastructure.ai.routing.provider_scorer import (
    ProviderScorer,
)

from app.infrastructure.ai.routing.routing_engine import (
    RoutingEngine,
)

from app.infrastructure.monitoring.metrics_registry import (
    MetricsRegistry,
)

from app.infrastructure.repositories.memory.in_memory_incident_repository import (
    InMemoryIncidentRepository,
)

from app.infrastructure.repositories.mongo.mongo_incident_repository import (
    MongoIncidentRepository,
)

from app.application.services.provider_monitoring_service import (
    ProviderMonitoringService,
)

# ------------------------------------------------------------------
# Repository
# ------------------------------------------------------------------


def get_incident_repository() -> IncidentRepository:

    if settings.REPOSITORY_TYPE.lower() == "mongo":
        return MongoIncidentRepository()

    return InMemoryIncidentRepository()


# ------------------------------------------------------------------
# Incident CRUD Service
# ------------------------------------------------------------------


def get_incident_service() -> IncidentService:

    return IncidentService(
        repository=get_incident_repository(),
    )


# ------------------------------------------------------------------
# AI Providers
# ------------------------------------------------------------------


@lru_cache
def get_gemini_provider() -> GeminiProvider:
    return GeminiProvider()


@lru_cache
def get_openrouter_provider() -> OpenRouterProvider:
    return OpenRouterProvider()


# ------------------------------------------------------------------
# Provider Registry
# ------------------------------------------------------------------


@lru_cache
def get_provider_registry() -> ProviderRegistry:

    registry = ProviderRegistry()

    registry.register(
        "gemini",
        get_gemini_provider(),
    )

    registry.register(
        "openrouter",
        get_openrouter_provider(),
    )

    return registry


# ------------------------------------------------------------------
# NEW
# Provider Metadata Registry
# ------------------------------------------------------------------


@lru_cache
def get_provider_metadata_registry() -> ProviderMetadataRegistry:

    registry = ProviderMetadataRegistry()

    registry.register(
        ProviderMetadata(
            name="gemini",
            display_name="Google Gemini",
            model="gemini-2.0-flash",
            priority=1,
            input_cost_per_1k_tokens=0.000075,
            output_cost_per_1k_tokens=0.0003,
            max_context_tokens=1_000_000,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                    ProviderCapability.STRUCTURED_OUTPUT,
                    ProviderCapability.FUNCTION_CALLING,
                    ProviderCapability.STREAMING,
                    ProviderCapability.LONG_CONTEXT,
                }
            ),
        )
    )

    registry.register(
        ProviderMetadata(
            name="openrouter",
            display_name="OpenRouter",
            model=settings.OPENROUTER_MODEL,
            priority=2,
            input_cost_per_1k_tokens=0.0,
            output_cost_per_1k_tokens=0.0,
            max_context_tokens=8192,
            capabilities=frozenset(
                {
                    ProviderCapability.TEXT_GENERATION,
                    ProviderCapability.STREAMING,
                }
            ),
        )
    )

    return registry


# ------------------------------------------------------------------
# Health Service
# ------------------------------------------------------------------


@lru_cache
def get_provider_health_service() -> ProviderHealthService:

    return ProviderHealthService()


# ------------------------------------------------------------------
# Metrics Service
# ------------------------------------------------------------------


@lru_cache
def get_provider_metrics_service() -> ProviderMetricsService:

    return ProviderMetricsService()


# ------------------------------------------------------------------
# NEW
# Provider Scorer
# ------------------------------------------------------------------


@lru_cache
def get_provider_scorer() -> ProviderScorer:

    return ProviderScorer(
        metadata_registry=get_provider_metadata_registry(),
    )


# ------------------------------------------------------------------
# NEW
# Routing Engine
# ------------------------------------------------------------------


@lru_cache
def get_routing_engine() -> RoutingEngine:

    return RoutingEngine(
        registry=get_provider_registry(),
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
        scorer=get_provider_scorer(),
    )


# ------------------------------------------------------------------
# Routing Policy
# ------------------------------------------------------------------


@lru_cache
def get_routing_policy() -> PriorityRoutingPolicy:

    return PriorityRoutingPolicy(
        registry=get_provider_registry(),
        routing_engine=get_routing_engine(),
    )


# ------------------------------------------------------------------
# AI Router
# ------------------------------------------------------------------


@lru_cache
def get_metrics_registry() -> MetricsRegistry:

    return MetricsRegistry(
        metadata_registry=get_provider_metadata_registry(),
    )


@lru_cache
def get_ai_router() -> AIRouter:

    return AIRouter(
        registry=get_provider_registry(),
        routing_policy=get_routing_policy(),
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
        metrics_registry=get_metrics_registry(),
        cache=get_semantic_cache(),
        tracer=get_tracer(),
    )

# ------------------------------------------------------------------
# Provider Monitoring Service
# ------------------------------------------------------------------


@lru_cache
def get_provider_monitoring_service() -> ProviderMonitoringService:

    return ProviderMonitoringService(
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
    )


# ------------------------------------------------------------------
# Provider Bootstrap
# ------------------------------------------------------------------


@lru_cache
def get_provider_bootstrap() -> ProviderBootstrap:

    return ProviderBootstrap(
        registry=get_provider_registry(),
        health_service=get_provider_health_service(),
        metrics_service=get_provider_metrics_service(),
    )

# ------------------------------------------------------------------
# AI Agent
# ------------------------------------------------------------------


@lru_cache
def get_incident_agent() -> IncidentAgent:

    return IncidentAgent(
        ai_service=get_ai_router(),
    )


# ------------------------------------------------------------------
# Incident Analysis Service
# ------------------------------------------------------------------


@lru_cache
def get_incident_analysis_service() -> IncidentAnalysisService:

    return IncidentAnalysisService(
        agent=get_incident_agent(),
    )


# ------------------------------------------------------------------
# Agent Framework
# ------------------------------------------------------------------


@lru_cache
def get_agent_registry() -> AgentRegistry:

    from app.infrastructure.ai.agents.analysis_agent import (
        AnalysisAgent,
    )
    from app.infrastructure.ai.agents.recommendation_agent import (
        RecommendationAgent,
    )
    from app.infrastructure.ai.agents.triage_agent import (
        TriageAgent,
    )
    from app.infrastructure.adk.adk_agent import AdkAgent

    registry = AgentRegistry()

    registry.register(TriageAgent())

    registry.register(
        AnalysisAgent(
            ai_service=get_ai_router(),
        )
    )

    registry.register(RecommendationAgent())

    registry.register(
        get_knowledge_retrieval_agent()
    )

    registry.register(
        AdkAgent(
            name="adk_investigator",
            instruction=(
                "Investigate the incident and produce a concise "
                "root-cause summary from the available context."
            ),
            description="Google ADK investigation agent.",
            order=5,
        )
    )

    return registry


@lru_cache
def get_agent_orchestrator() -> AgentOrchestrator:

    return AgentOrchestrator(
        registry=get_agent_registry(),
    )


@lru_cache
def get_adk_orchestrator() -> AdkOrchestrator:

    from app.infrastructure.adk.adk_agent import AdkAgent

    return AdkOrchestrator(
        agents=[
            AdkAgent(
                name="adk_investigator",
                instruction=(
                    "Investigate the incident and produce a concise "
                    "root-cause summary from the available context."
                ),
                description="Google ADK investigation agent.",
                order=5,
            )
        ],
    )


# ------------------------------------------------------------------
# Workflow Engine
# ------------------------------------------------------------------


@lru_cache
def get_workflow_engine() -> WorkflowEngine:

    return WorkflowEngine(
        orchestrator=get_agent_orchestrator(),
    )


@lru_cache
def get_incident_workflow() -> IncidentWorkflow:

    return IncidentWorkflow(
        engine=get_workflow_engine(),
        registry=get_agent_registry(),
    )


# ------------------------------------------------------------------
# Knowledge Memory Layer
# ------------------------------------------------------------------


@lru_cache
def get_embedding_service() -> EmbeddingService:

    if settings.EMBEDDING_PROVIDER.lower() == "gemini":

        from app.infrastructure.knowledge.embeddings.gemini_embedding_service import (
            GeminiEmbeddingService,
        )

        return GeminiEmbeddingService()

    return HashingEmbeddingService()


@lru_cache
def get_vector_repository() -> VectorRepository:

    if settings.REPOSITORY_TYPE.lower() == "mongo":

        from app.infrastructure.knowledge.vector.mongo_vector_repository import (
            MongoVectorRepository,
        )

        return MongoVectorRepository()

    from app.infrastructure.knowledge.vector.in_memory_vector_repository import (
        InMemoryVectorRepository,
    )

    return InMemoryVectorRepository()


@lru_cache
def get_knowledge_base_service() -> KnowledgeBaseService:

    return KnowledgeBaseService(
        repository=get_vector_repository(),
        embedding_service=get_embedding_service(),
    )


@lru_cache
def get_document_ingestion_pipeline() -> DocumentIngestionPipeline:

    return DocumentIngestionPipeline(
        knowledge_base=get_knowledge_base_service(),
    )


@lru_cache
def get_incident_memory_repository() -> IncidentMemoryRepository:

    if settings.REPOSITORY_TYPE.lower() == "mongo":

        from app.infrastructure.knowledge.incident_memory.mongo_incident_memory_repository import (
            MongoIncidentMemoryRepository,
        )

        return MongoIncidentMemoryRepository()

    from app.infrastructure.knowledge.incident_memory.in_memory_incident_memory_repository import (
        InMemoryIncidentMemoryRepository,
    )

    return InMemoryIncidentMemoryRepository()


@lru_cache
def get_incident_memory_service() -> IncidentMemoryService:

    return IncidentMemoryService(
        repository=get_incident_memory_repository(),
    )


@lru_cache
def get_knowledge_retrieval_agent() -> KnowledgeRetrievalAgent:

    return KnowledgeRetrievalAgent(
        knowledge_base=get_knowledge_base_service(),
    )


# ------------------------------------------------------------------
# Tool Execution Framework
# ------------------------------------------------------------------


@lru_cache
def get_approval_workflow() -> ApprovalWorkflow:

    return ApprovalWorkflow()


@lru_cache
def get_tool_registry() -> ToolRegistry:

    from app.infrastructure.tools.aws.aws_tool import AWSTool
    from app.infrastructure.tools.azure.azure_tool import AzureTool
    from app.infrastructure.tools.jira.jira_tool import JiraTool
    from app.infrastructure.tools.kubernetes.kubernetes_tool import (
        KubernetesTool,
    )
    from app.infrastructure.tools.servicenow.servicenow_tool import (
        ServiceNowTool,
    )
    from app.infrastructure.tools.slack.slack_tool import SlackTool
    from app.infrastructure.tools.teams.teams_tool import TeamsTool
    from app.infrastructure.tools.transport import SimulatedTransport

    registry = ToolRegistry()

    demo = SimulatedTransport()

    registry.register(ServiceNowTool(transport=demo))
    registry.register(JiraTool(transport=demo))
    registry.register(AWSTool(transport=demo))
    registry.register(AzureTool(transport=demo))
    registry.register(KubernetesTool(transport=demo))
    registry.register(SlackTool(transport=demo))
    registry.register(TeamsTool(transport=demo))

    return registry


@lru_cache
def get_tool_executor() -> ToolExecutor:

    return ToolExecutor(
        registry=get_tool_registry(),
        approval=get_approval_workflow(),
        tracer=get_tracer(),
    )


# ------------------------------------------------------------------
# Governance & Security Layer
# ------------------------------------------------------------------


@lru_cache
def get_rbac_service() -> RbacService:

    return RbacService()


@lru_cache
def get_audit_log_service() -> AuditLogService:

    return AuditLogService()


@lru_cache
def get_approval_policy_engine() -> ApprovalPolicyEngine:

    engine = ApprovalPolicyEngine()

    engine.register_action(
        "incident.analyze",
        RiskLevel.LOW,
    )

    engine.register_action(
        "tool.servicenow.create_incident",
        RiskLevel.LOW,
    )

    engine.register_action(
        "tool.servicenow.resolve_incident",
        RiskLevel.MEDIUM,
    )

    engine.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    engine.register_action(
        "tool.aws.delete",
        RiskLevel.HIGH,
    )

    engine.register_action(
        "tool.database.execute",
        RiskLevel.HIGH,
    )

    return engine


@lru_cache
def get_prompt_registry() -> PromptRegistry:

    return PromptRegistry()


@lru_cache
def get_model_governance_service() -> ModelGovernanceService:

    return ModelGovernanceService()


@lru_cache
def get_data_privacy_service() -> DataPrivacyService:

    return DataPrivacyService()


# ------------------------------------------------------------------
# Self-Learning Optimization Engine
# ------------------------------------------------------------------


@lru_cache
def get_feedback_engine() -> FeedbackEngine:

    return FeedbackEngine()


@lru_cache
def get_evaluation_engine() -> EvaluationEngine:

    return EvaluationEngine()


@lru_cache
def get_routing_optimizer() -> RoutingOptimizer:

    optimizer = RoutingOptimizer()

    for provider_name in get_provider_registry().list():
        optimizer.register_provider(provider_name)

    return optimizer


@lru_cache
def get_prompt_optimizer() -> PromptOptimizer:

    return PromptOptimizer()


@lru_cache
def get_agent_analytics() -> AgentAnalytics:

    return AgentAnalytics()


@lru_cache
def get_cost_optimizer() -> CostOptimizer:

    optimizer = CostOptimizer()

    metadata_registry = get_provider_metadata_registry()

    for provider_name in metadata_registry.list():

        metadata = metadata_registry.get(provider_name)

        optimizer.register_model(
            provider=metadata.name,
            model=metadata.model,
            input_cost_per_1k_tokens=(
                metadata.input_cost_per_1k_tokens
            ),
            output_cost_per_1k_tokens=(
                metadata.output_cost_per_1k_tokens
            ),
            capabilities=metadata.capabilities,
        )

    return optimizer


# ------------------------------------------------------------------
# Autonomous AIOps Execution Engine
# ------------------------------------------------------------------


@lru_cache
def get_event_ingestion_engine() -> EventIngestionEngine:

    return EventIngestionEngine()


@lru_cache
def get_risk_based_executor() -> RiskBasedExecutor:

    executor = RiskBasedExecutor(
        policy=get_approval_policy_engine(),
    )

    executor.register_action(
        "tool.kubernetes.pod_status",
        RiskLevel.LOW,
    )

    executor.register_action(
        "tool.kubernetes.logs",
        RiskLevel.LOW,
    )

    executor.register_action(
        "tool.servicenow.create_incident",
        RiskLevel.LOW,
    )

    executor.register_action(
        "tool.kubernetes.restart",
        RiskLevel.MEDIUM,
    )

    executor.register_action(
        "tool.kubernetes.scale",
        RiskLevel.MEDIUM,
    )

    executor.register_action(
        "tool.aws.delete",
        RiskLevel.HIGH,
    )

    return executor


@lru_cache
def get_playbook_engine() -> RemediationPlaybookEngine:

    engine = RemediationPlaybookEngine()

    engine.load_yaml(
        """
name: kubernetes_crash_restart
description: Restart a crashing Kubernetes deployment
version: 1.0.0
match:
  source: kubernetes
  severities:
    - high
    - medium
  tags:
    - crash
    - restart
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
  - name: restart_deployment
    tool: kubernetes
    action: restart
    risk_level: medium
    auto_execute: false
"""
    )

    engine.load_yaml(
        """
name: memory_restart
description: Restart a pod under memory pressure
version: 1.0.0
match:
  source: kubernetes
  severities:
    - high
  tags:
    - memory
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
  - name: restart_pod
    tool: kubernetes
    action: restart
    risk_level: medium
    auto_execute: false
"""
    )

    # Fully autonomous playbook — every step is low-risk (auto-executed),
    # so a matching alert completes the lifecycle with ZERO human approval.
    engine.load_yaml(
        """
name: kubernetes_health_check
description: Low-risk health inspection of a Kubernetes workload
version: 1.0.0
match:
  source: kubernetes
  severities:
    - low
    - medium
  tags:
    - health
    - status
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
    auto_execute: true
  - name: fetch_logs
    tool: kubernetes
    action: logs
    parameters:
      pod_name: payments-7d9b5c4f6-2xk9p
    risk_level: low
    auto_execute: true
  - name: create_snow_incident
    tool: servicenow
    action: create_incident
    risk_level: low
    auto_execute: true
"""
    )

    return engine


@lru_cache
def get_autonomous_decision_engine() -> AutonomousDecisionEngine:

    return AutonomousDecisionEngine(
        risk_executor=get_risk_based_executor(),
    )


@lru_cache
def get_multi_agent_runner() -> AioOpsMultiAgentRunner:

    return AioOpsMultiAgentRunner(
        agents=[
            AioOpsIncidentAgent(),
            AioOpsRcaAgent(),
            AioOpsPlannerAgent(),
            AioOpsExecutionAgent(
                executor=get_tool_executor(),
            ),
            AioOpsVerificationAgent(),
        ]
    )


@lru_cache
def get_incident_lifecycle_orchestrator() -> IncidentLifecycleOrchestrator:

    return IncidentLifecycleOrchestrator(
        ingestion=get_event_ingestion_engine(),
        decision_engine=get_autonomous_decision_engine(),
        playbooks=get_playbook_engine(),
        agents=get_multi_agent_runner(),
        feedback=get_feedback_engine(),
        evaluation=get_evaluation_engine(),
        executor=get_tool_executor(),
        publisher=get_event_publisher(),
    )


# ------------------------------------------------------------------
# Reliability & Resilience Engine
# ------------------------------------------------------------------


@lru_cache
def get_workflow_recovery() -> WorkflowRecovery:

    return WorkflowRecovery()


@lru_cache
def get_remediation_rollback() -> RemediationRollback:

    return RemediationRollback()


@lru_cache
def get_root_cause_graph() -> RootCauseGraph:

    return RootCauseGraph()


@lru_cache
def get_dependency_intelligence() -> DependencyIntelligence:

    return DependencyIntelligence()


@lru_cache
def get_incident_correlation() -> IncidentCorrelation:

    return IncidentCorrelation()


@lru_cache
def get_business_impact_analysis() -> BusinessImpactAnalysis:

    return BusinessImpactAnalysis()


@lru_cache
def get_chaos_testing_simulator() -> ChaosTestingSimulator:

    return ChaosTestingSimulator()


# ------------------------------------------------------------------
# Advanced AI Reasoning & Decision Intelligence Engine
# ------------------------------------------------------------------


@lru_cache
def get_decision_confidence_engine() -> DecisionConfidenceEngine:

    return DecisionConfidenceEngine()


@lru_cache
def get_decision_explainer() -> DecisionExplainer:

    return DecisionExplainer()


@lru_cache
def get_self_verification_layer() -> SelfVerificationLayer:

    return SelfVerificationLayer()


@lru_cache
def get_reasoning_history_store() -> ReasoningHistoryStore:

    return ReasoningHistoryStore()


@lru_cache
def get_dynamic_model_selector() -> DynamicModelSelector:

    selector = DynamicModelSelector()

    metadata_registry = get_provider_metadata_registry()

    for provider_name in metadata_registry.list():

        metadata = metadata_registry.get(provider_name)

        if metadata is None:
            continue

        selector.register_complex_model(
            name=metadata.name,
            model=metadata.model,
            provider=metadata.name,
            input_cost_per_1k_tokens=(
                metadata.input_cost_per_1k_tokens
            ),
            output_cost_per_1k_tokens=(
                metadata.output_cost_per_1k_tokens
            ),
        )

    selector.register_simple_model(
        name="gemini",
        model="gemini-2.0-flash",
        provider="gemini",
        input_cost_per_1k_tokens=0.000075,
        output_cost_per_1k_tokens=0.0003,
    )

    return selector


@lru_cache
def get_multi_agent_reasoning_runner() -> MultiAgentReasoningRunner:

    return MultiAgentReasoningRunner(
        agents=[
            ReasoningIncidentAnalysisAgent(
                engine=get_autonomous_decision_engine(),
            ),
            ReasoningRcaAgent(),
            ReasoningVerificationAgent(
                verification=get_self_verification_layer(),
            ),
            ReasoningDecisionAgent(
                confidence_engine=(
                    get_decision_confidence_engine()
                ),
                explainer=get_decision_explainer(),
            ),
        ]
    )


@lru_cache
def get_reasoning_orchestrator() -> ReasoningOrchestrator:

    return ReasoningOrchestrator(
        runner=get_multi_agent_reasoning_runner(),
        history=get_reasoning_history_store(),
        model_selector=get_dynamic_model_selector(),
        publisher=get_event_publisher(),
    )


# ------------------------------------------------------------------
# Real-Time Operations Command Center
# ------------------------------------------------------------------


@lru_cache
def get_event_publisher() -> EventPublisher:

    return EventPublisher()


@lru_cache
def get_incident_timeline() -> IncidentTimeline:

    return IncidentTimeline()


@lru_cache
def get_activity_feed() -> ActivityFeed:

    return ActivityFeed()


@lru_cache
def get_execution_monitor() -> ExecutionMonitor:

    return ExecutionMonitor()


@lru_cache
def get_operations_dashboard() -> OperationsDashboard:

    return OperationsDashboard(
        incident_service=get_incident_service(),
        agent_analytics=get_agent_analytics(),
        rollback=get_remediation_rollback(),
    )


@lru_cache
def get_operations_command_center() -> OperationsCommandCenter:

    return OperationsCommandCenter(
        publisher=get_event_publisher(),
        timeline=get_incident_timeline(),
        activity=get_activity_feed(),
        monitor=get_execution_monitor(),
        dashboard=get_operations_dashboard(),
    )


# ==========================================================
# Cache Layer
# ==========================================================


@lru_cache
def get_cache_service() -> CacheService:
    """
    Returns the configured cache backend.

    Falls back to the in-memory cache when Redis is not
    installed or not configured.
    """

    redis_client = None

    try:

        from app.core.config import settings as _settings

        if _settings.CACHE_URL:

            import redis

            redis_client = redis.from_url(
                _settings.CACHE_URL,
                decode_responses=True,
            )

    except Exception:
        redis_client = None

    if redis_client is not None:

        return RedisCacheService(client=redis_client)

    return InMemoryCacheService()


@lru_cache
def get_semantic_cache() -> SemanticCache:

    return SemanticCache(
        cache=get_cache_service(),
        similarity_threshold=0.90,
    )


@lru_cache
def get_prompt_cache() -> PromptCache:

    return PromptCache(
        cache=get_cache_service(),
        default_ttl_seconds=3600,
    )


@lru_cache
def get_cache_key_builder() -> CacheKeyBuilder:

    return CacheKeyBuilder()


# ==========================================================
# Tracing Layer
# ==========================================================


@lru_cache
def get_tracer() -> Tracer:

    return Tracer(
        service_name=settings.APP_NAME,
        enabled=(
            settings.ENVIRONMENT.lower() != "test"
        ),
    )
