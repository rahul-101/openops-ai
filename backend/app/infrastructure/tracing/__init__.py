"""
Distributed tracing layer.

Provides an in-memory Tracer and SpanBuilder for instrumenting
AI requests, tool executions and workflow steps. Spans capture
hierarchy, attributes, events and durations, and can be exported
as plain dicts or to OpenTelemetry backends.
"""

from app.infrastructure.tracing.span_builder import (
    SpanBuilder,
)
from app.infrastructure.tracing.tracer import (
    Tracer,
)

__all__ = [
    "SpanBuilder",
    "Tracer",
]
