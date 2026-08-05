from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Optional

from app.core.config import settings
from app.infrastructure.persistence import (
    from_jsonable,
    new_store,
    to_jsonable,
)
from app.infrastructure.persistence.mongodb import get_database

_LIST_KEY = "__all__"


@dataclass
class ModelUsageRecord:
    """
    A single model invocation for governance tracking.
    """

    provider: str

    model: str

    input_tokens: int = 0

    output_tokens: int = 0

    cost_usd: float = 0.0

    latency_ms: float = 0.0

    action: str | None = None

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )


class ModelGovernanceService:
    """
    Tracks model usage, provider selection, cost and
    performance across AI calls.
    """

    def __init__(self) -> None:

        self._records: list[ModelUsageRecord] = []

        self._lock = Lock()

        self._store = new_store("model_usage")

        self._mongo_repo = None
        if settings.REPOSITORY_TYPE.lower() == "mongo":
            from app.infrastructure.governance.mongo_model_governance_repository import (
                MongoModelGovernanceRepository,
            )
            self._mongo_repo = MongoModelGovernanceRepository()

        if self._store is not None:

            blob = self._store.get(_LIST_KEY) or {}

            self._records = []

            for record in blob.get("records", []):

                parsed = from_jsonable(
                    record,
                    ModelUsageRecord,
                )

                if parsed is not None:
                    self._records.append(parsed)

    def _persist(self) -> None:

        if self._store is not None:
            self._store.save(
                _LIST_KEY,
                {
                    "records": [
                        to_jsonable(record)
                        for record in self._records
                    ]
                },
            )

    def record_usage(
        self,
        *,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        action: str | None = None,
    ) -> ModelUsageRecord:

        record = ModelUsageRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            action=action,
        )

        with self._lock:
            self._records.append(record)

        self._persist()

        if self._mongo_repo is not None:
            self._mongo_repo.insert(record)

        return record

    def list(
        self,
        provider: str | None = None,
        model: str | None = None,
        limit: int | None = None,
    ) -> list[ModelUsageRecord]:

        if self._mongo_repo is not None:
            return self._mongo_repo.list(
                provider=provider,
                model=model,
                limit=limit,
            )

        with self._lock:

            records = [
                record
                for record in self._records
                if (
                    provider is None
                    or record.provider == provider
                )
                and (
                    model is None
                    or record.model == model
                )
            ]

        if limit is not None:
            records = records[-limit:]

        return list(records)

    def get_stats(
        self,
        provider: str | None = None,
    ) -> dict:

        records = self.list(provider=provider)

        if not records:

            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "average_latency_ms": 0.0,
                "providers": {},
            }

        total_input = sum(
            r.input_tokens for r in records
        )

        total_output = sum(
            r.output_tokens for r in records
        )

        average_latency = (
            sum(r.latency_ms for r in records)
            / len(records)
        )

        by_provider: dict[str, dict] = {}

        for record in records:

            stats = by_provider.setdefault(
                record.provider,
                {
                    "requests": 0,
                    "cost_usd": 0.0,
                    "tokens": 0,
                },
            )

            stats["requests"] += 1
            stats["cost_usd"] += record.cost_usd
            stats["tokens"] += (
                record.input_tokens + record.output_tokens
            )

        return {
            "total_requests": len(records),
            "total_tokens": total_input + total_output,
            "total_cost_usd": sum(
                r.cost_usd for r in records
            ),
            "average_latency_ms": average_latency,
            "providers": by_provider,
        }

    def clear(self) -> None:

        with self._lock:
            self._records.clear()

        if self._store is not None:
            self._store.clear()

        if self._mongo_repo is not None:
            self._mongo_repo.clear()
