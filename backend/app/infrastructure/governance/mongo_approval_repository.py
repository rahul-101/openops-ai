from app.core.config import settings
from app.infrastructure.governance.models import RiskLevel
from app.infrastructure.persistence.mongodb import get_database


class MongoApprovalRepository:
    """
    MongoDB persistence for approval policy actions.
    """

    def __init__(self) -> None:
        self.collection = get_database()[
            settings.APPROVAL_COLLECTION
        ]

    def save_action(
        self,
        action: str,
        risk_level: RiskLevel,
    ) -> None:
        self.collection.update_one(
            {"action": action.lower()},
            {
                "$set": {
                    "action": action.lower(),
                    "risk_level": risk_level.value,
                }
            },
            upsert=True,
        )

    def get_risk_level(self, action: str) -> RiskLevel | None:
        document = self.collection.find_one(
            {"action": action.lower()}
        )
        if document is None:
            return None
        return RiskLevel(document["risk_level"])

    def get_all_actions(self) -> dict[str, RiskLevel]:
        cursor = self.collection.find({})
        return {
            doc["action"]: RiskLevel(doc["risk_level"])
            for doc in cursor
        }

    def delete_action(self, action: str) -> None:
        self.collection.delete_one(
            {"action": action.lower()}
        )

    def clear(self) -> None:
        self.collection.delete_many({})