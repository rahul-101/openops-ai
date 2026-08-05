from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.infrastructure.governance.model_governance import ModelUsageRecord
from app.infrastructure.persistence.mongodb import get_database


class MongoModelGovernanceRepository:
    """
    MongoDB persistence for model governance records.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.MODEL_GOVERNANCE_COLLECTION
        ]

    def _to_document(self, record: ModelUsageRecord) -> dict:
        return {
            "provider": record.provider,
            "model": record.model,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "cost_usd": record.cost_usd,
            "latency_ms": record.latency_ms,
            "action": record.action,
            "timestamp": record.timestamp,
        }

    def _from_document(self, document: dict) -> ModelUsageRecord:
        document.pop("_id", None)
        return ModelUsageRecord(**document)

    def insert(self, record: ModelUsageRecord) -> None:
        self.collection.insert_one(self._to_document(record))

    def list(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[ModelUsageRecord]:
        query = {}
        if provider is not None:
            query["provider"] = provider
        if model is not None:
            query["model"] = model

        cursor = self.collection.find(query).sort("timestamp", -1)

        if limit is not None:
            cursor = cursor.limit(limit)

        return [self._from_document(doc) for doc in cursor]

    def clear(self) -> None:
        self.collection.delete_many({})