import asyncio

import pytest

from app.infrastructure.tracing.span_builder import (
    SpanBuilder,
)
from app.infrastructure.tracing.tracer import (
    Tracer,
)


class TestSpanBuilder:

    def test_duration_ms_positive(self):

        span = SpanBuilder(name="op")

        span.finish()

        assert span.duration_ms >= 0.0

    def test_finish_is_idempotent(self):

        span = SpanBuilder(name="op")

        span.finish()

        first = span.duration_ms

        span.finish()

        assert span.duration_ms == first

    def test_set_attribute(self):

        span = SpanBuilder(name="op")

        span.set_attribute("key", 42)

        assert span.attributes == {"key": "42"}

    def test_add_event(self):

        span = SpanBuilder(name="op")

        span.add_event("started", {"step": 1})

        assert span.events == [("started", {"step": 1})]

    def test_record_error(self):

        span = SpanBuilder(name="op")

        span.record_error(ValueError("boom"))

        assert span.error == "boom"

        assert span.events[-1][0] == "error"

    def test_to_dict_shape(self):

        span = SpanBuilder(name="op")

        span.set_attribute("a", "b")

        span.finish()

        payload = span.to_dict()

        assert payload["name"] == "op"

        assert payload["attributes"] == {"a": "b"}

        assert payload["is_finished"] is True

        assert "span_id" in payload

    def test_child_links_parent(self):

        parent = SpanBuilder(name="parent")

        child = parent.child("child")

        assert child.parent_id == parent.span_id


class TestTracer:

    def test_start_span_tracks(self):

        tracer = Tracer()

        span = tracer.start_span("op")

        assert span.name == "op"

        assert tracer.size() == 1

    def test_active_nesting(self):

        tracer = Tracer()

        outer = tracer.start_span("outer")

        inner = tracer.start_span("inner")

        assert inner.parent_id == outer.span_id

        tracer.end_span(inner)

        tracer.end_span(outer)

    def test_end_span_marks_finished(self):

        tracer = Tracer()

        span = tracer.start_span("op")

        tracer.end_span(span)

        assert span.is_finished is True

        assert tracer.active_count() == 0

    def test_context_manager_times_block(self):

        tracer = Tracer()

        with tracer.span("block") as span:

            span.set_attribute("a", "b")

        assert len(tracer.spans()) == 1

        assert tracer.spans()[0].is_finished is True

        assert tracer.spans()[0].attributes == {"a": "b"}

    def test_context_manager_records_error(self):

        tracer = Tracer()

        with pytest.raises(RuntimeError):

            with tracer.span("block"):
                raise RuntimeError("boom")

        span = tracer.spans()[0]

        assert span.error == "boom"

        assert span.is_finished is True

    def test_clear(self):

        tracer = Tracer()

        tracer.start_span("op")

        tracer.clear()

        assert tracer.size() == 0

    def test_export_only_finished(self):

        tracer = Tracer()

        span = tracer.start_span("op")

        tracer.end_span(span)

        tracer.start_span("running")

        exported = tracer.export()

        assert len(exported) == 1

    def test_disabled_tracer_still_records(self):

        # enabled flag is a hint; tracer remains functional
        tracer = Tracer(enabled=True)

        tracer.start_span("op")

        assert tracer.size() == 1


@pytest.mark.asyncio
class TestTracerAsync:

    async def test_async_instrument(self):

        tracer = Tracer()

        async with tracer.instrument_async("ai.request"):
            await asyncio.sleep(0.01)

        spans = tracer.spans()

        assert len(spans) == 1

        assert spans[0].name == "ai.request"

        assert spans[0].is_finished is True

        assert "duration_ms" in spans[0].attributes

    async def test_async_instrument_records_error(self):

        tracer = Tracer()

        with pytest.raises(ValueError):

            async with tracer.instrument_async("ai.request"):
                raise ValueError("bad")

        assert tracer.spans()[0].error == "bad"
