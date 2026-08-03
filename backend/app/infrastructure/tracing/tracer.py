from threading import Lock
from time import perf_counter

from app.infrastructure.tracing.span_builder import (
    SpanBuilder,
)


class Tracer:
    """
    Lightweight distributed tracer.

    Maintains a thread-safe span store and exposes a context
    manager for timing operations. Backed by in-memory spans
    by default; can optionally export to OpenTelemetry when a
    collector/exporter is configured.
    """

    def __init__(
        self,
        service_name: str = "openops-ai",
        enabled: bool = True,
    ) -> None:

        self.service_name = service_name

        self.enabled = enabled

        self._spans: list[SpanBuilder] = []

        self._active: list[SpanBuilder] = []

        self._lock = Lock()

        self._collector = None

    # ==========================================================
    # Span lifecycle
    # ==========================================================

    def start_span(
        self,
        name: str,
        attributes: dict | None = None,
    ) -> SpanBuilder:
        """
        Starts a span, nesting under the currently active span.
        """

        with self._lock:

            parent = self._active[-1] if self._active else None

            span = SpanBuilder(
                name=name,
                parent_id=parent.span_id if parent else None,
            )

            for key, value in (attributes or {}).items():
                span.set_attribute(key, value)

            self._spans.append(span)

            self._active.append(span)

            return span

    def end_span(
        self,
        span: SpanBuilder,
    ) -> None:

        span.finish()

        with self._lock:

            if span in self._active:
                self._active.remove(span)

    def span(
        self,
        name: str,
        attributes: dict | None = None,
    ):
        """
        Context manager for a traced operation.
        """

        return _SpanContext(self, name, attributes)

    # ==========================================================
    # Readouts
    # ==========================================================

    def spans(
        self,
        limit: int | None = None,
    ) -> list[SpanBuilder]:

        with self._lock:

            spans = list(self._spans)

        if limit is not None:
            spans = spans[-limit:]

        return spans

    def active_count(self) -> int:

        with self._lock:
            return len(self._active)

    def clear(self) -> None:

        with self._lock:

            self._spans.clear()

            self._active.clear()

    def size(self) -> int:

        with self._lock:
            return len(self._spans)

    def export(self) -> list[dict]:
        """
        Returns all completed spans as dicts.
        """

        return [
            span.to_dict()
            for span in self.spans()
            if span.is_finished
        ]

    # ==========================================================
    # Instrumentation helpers
    # ==========================================================

    def instrument_async(self, name: str):
        """
        Async context manager that times a coroutine.
        """

        return _AsyncSpanContext(self, name)


class _SpanContext:
    """
    Synchronous context manager for timing a block.
    """

    def __init__(
        self,
        tracer: Tracer,
        name: str,
        attributes: dict | None = None,
    ) -> None:

        self.tracer = tracer

        self.name = name

        self.attributes = attributes

        self.span: SpanBuilder | None = None

    def __enter__(self) -> SpanBuilder:

        self.span = self.tracer.start_span(
            self.name,
            attributes=self.attributes,
        )

        return self.span

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        if exc_value is not None and self.span is not None:

            self.span.record_error(exc_value)

        if self.span is not None:

            self.tracer.end_span(self.span)


class _AsyncSpanContext:
    """
    Async context manager for timing an awaited operation.
    """

    def __init__(
        self,
        tracer: Tracer,
        name: str,
    ) -> None:

        self.tracer = tracer

        self.name = name

        self.start = 0.0

    async def __aenter__(self) -> None:

        self.start = perf_counter()

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        span = self.tracer.start_span(self.name)

        span.set_attribute(
            "duration_ms",
            round(
                max(
                    (perf_counter() - self.start) * 1000,
                    0.0,
                ),
                3,
            ),
        )

        if exc_value is not None:
            span.record_error(exc_value)

        self.tracer.end_span(span)
