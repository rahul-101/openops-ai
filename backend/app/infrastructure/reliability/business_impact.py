from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock


class ImpactSeverity(str, Enum):
    """
    Business impact severity of an incident.
    """

    SEV1 = "sev1"

    SEV2 = "sev2"

    SEV3 = "sev3"


class SlaStatus(str, Enum):
    """
    SLA breach status for an incident.
    """

    WITHIN_SLA = "within_sla"

    AT_RISK = "at_risk"

    BREACHED = "breached"


@dataclass
class BusinessImpact:
    """
    Calculated business impact for an incident.
    """

    incident_id: str

    severity: ImpactSeverity

    sla_status: SlaStatus

    affected_users: int = 0

    revenue_at_risk: float = 0.0

    response_time_sla_minutes: int = 0

    elapsed_minutes: int = 0

    score: float = 0.0

    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class BusinessImpactAnalysis:
    """
    Calculates severity and SLA impact for incidents.

    Severity is derived from affected users and revenue.
    SLA impact is derived from the elapsed time versus the
    configured response SLA.
    """

    #: Sev thresholds
    SEV1_REVENUE_THRESHOLD = 100_000.0

    SEV2_REVENUE_THRESHOLD = 10_000.0

    SEV2_USERS_THRESHOLD = 1_000

    SEV3_USERS_THRESHOLD = 100

    def __init__(self) -> None:

        self._records: dict[str, BusinessImpact] = {}

        self._lock = Lock()

    def analyze(
        self,
        *,
        incident_id: str,
        affected_users: int = 0,
        revenue_at_risk: float = 0.0,
        response_time_sla_minutes: int = 60,
        elapsed_minutes: int = 0,
    ) -> BusinessImpact:

        severity = self._calculate_severity(
            affected_users,
            revenue_at_risk,
        )

        sla_status = self._calculate_sla_status(
            elapsed_minutes,
            response_time_sla_minutes,
        )

        impact = BusinessImpact(
            incident_id=incident_id,
            severity=severity,
            sla_status=sla_status,
            affected_users=affected_users,
            revenue_at_risk=revenue_at_risk,
            response_time_sla_minutes=response_time_sla_minutes,
            elapsed_minutes=elapsed_minutes,
            score=self._calculate_score(
                severity,
                sla_status,
            ),
        )

        with self._lock:
            self._records[incident_id] = impact

        return impact

    def get(
        self,
        incident_id: str,
    ) -> BusinessImpact | None:

        with self._lock:
            return self._records.get(incident_id)

    def list(self) -> list[BusinessImpact]:

        with self._lock:
            return list(self._records.values())

    def clear(self) -> None:

        with self._lock:
            self._records.clear()

    # ==========================================================
    # Calculation
    # ==========================================================

    @classmethod
    def _calculate_severity(
        cls,
        affected_users: int,
        revenue_at_risk: float,
    ) -> ImpactSeverity:

        if revenue_at_risk >= cls.SEV1_REVENUE_THRESHOLD:

            return ImpactSeverity.SEV1

        if (
            revenue_at_risk >= cls.SEV2_REVENUE_THRESHOLD
            or affected_users >= cls.SEV2_USERS_THRESHOLD
        ):

            return ImpactSeverity.SEV2

        if affected_users >= cls.SEV3_USERS_THRESHOLD:

            return ImpactSeverity.SEV3

        return ImpactSeverity.SEV3

    @staticmethod
    def _calculate_sla_status(
        elapsed_minutes: int,
        response_time_sla_minutes: int,
    ) -> SlaStatus:

        if response_time_sla_minutes <= 0:
            return SlaStatus.WITHIN_SLA

        ratio = elapsed_minutes / response_time_sla_minutes

        if ratio >= 1.0:
            return SlaStatus.BREACHED

        if ratio >= 0.8:
            return SlaStatus.AT_RISK

        return SlaStatus.WITHIN_SLA

    @staticmethod
    def _calculate_score(
        severity: ImpactSeverity,
        sla_status: SlaStatus,
    ) -> float:
        """
        Returns a normalized impact score in [0, 1].
        """

        severity_score = {
            ImpactSeverity.SEV1: 1.0,
            ImpactSeverity.SEV2: 0.6,
            ImpactSeverity.SEV3: 0.3,
        }[severity]

        sla_score = {
            SlaStatus.BREACHED: 1.0,
            SlaStatus.AT_RISK: 0.6,
            SlaStatus.WITHIN_SLA: 0.0,
        }[sla_status]

        return round(
            (severity_score * 0.6) + (sla_score * 0.4),
            2,
        )
