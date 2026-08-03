from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4


@dataclass
class SpanBuilder:
    """
    Builds and records a single trace span.

    Tracks hierarchy (parent/child), attributes, events and
    duration. Purely in-memory, so it can run without an
    OpenTelemetry collector and is easy to test.
    """

    name: str

    span_id: str = field(default_factory=lambda: str(uuid4()))

    parent_id: str | None = None

    attributes: dict = field(default_factory=dict)

    events: list[tuple[str, dict]] = field(default_factory=list)

    start_time: float = field(default_factory=perf_counter)

    end_time: float | None = None

    error: str | None = None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def set_attribute(
        self,
        key: str,
        value: object,
    ) -> None:

        self.attributes[key] = str(value)

    def add_event(
        self,
        name: str,
        attributes: dict | None = None,
    ) -> None:

        self.events.append(
            (name, dict(attributes or {}))
        )

    def record_error(
        self,
        error: Exception | str,
    ) -> None:

        self.error = str(error)

        self.add_event(
            "error",
            {"message": str(error)},
        )

    def finish(self) -> None:

        if self.end_time is None:
            self.end_time = perf_counter()

    # ==========================================================
    # Readouts
    # ==========================================================

    @property
    def duration_ms(self) -> float:

        end = self.end_time or perf_counter()

        return max((end - self.start_time) * 1000, 0.0)

    @property
    def is_finished(self) -> bool:

        return self.end_time is not None

    def to_dict(self) -> dict:

        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "attributes": dict(self.attributes),
            "events": [
                {"name": name, "attributes": attrs}
                for name, attrs in self.events
            ],
            "duration_ms": round(self.duration_ms, 3),
            "error": self.error,
            "is_finished": self.is_finished,
        }

    def child(
        self,
        name: str,
    ) -> "SpanBuilder":
        """
        Creates a child span linked to this span.
        """

        return SpanBuilder(
            name=name,
            parent_id=self.span_id,
        )
