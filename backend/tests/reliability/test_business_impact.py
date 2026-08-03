from app.infrastructure.reliability.business_impact import (
    BusinessImpactAnalysis,
    ImpactSeverity,
    SlaStatus,
)


def test_severity_sev1_high_revenue():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        revenue_at_risk=200_000.0,
    )

    assert impact.severity == ImpactSeverity.SEV1


def test_severity_sev2_many_users():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        affected_users=5_000,
    )

    assert impact.severity == ImpactSeverity.SEV2


def test_severity_sev3_low_impact():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        affected_users=50,
    )

    assert impact.severity == ImpactSeverity.SEV3


def test_sla_within():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        response_time_sla_minutes=60,
        elapsed_minutes=30,
    )

    assert impact.sla_status == SlaStatus.WITHIN_SLA


def test_sla_at_risk():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        response_time_sla_minutes=60,
        elapsed_minutes=50,
    )

    assert impact.sla_status == SlaStatus.AT_RISK


def test_sla_breached():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        response_time_sla_minutes=60,
        elapsed_minutes=90,
    )

    assert impact.sla_status == SlaStatus.BREACHED


def test_score_sev1_breach_is_high():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        revenue_at_risk=200_000.0,
        response_time_sla_minutes=60,
        elapsed_minutes=120,
    )

    assert impact.score == 1.0


def test_score_sev3_within_is_low():

    analysis = BusinessImpactAnalysis()

    impact = analysis.analyze(
        incident_id="inc-1",
        affected_users=10,
        response_time_sla_minutes=60,
        elapsed_minutes=10,
    )

    assert impact.score == 0.18


def test_get_and_list():

    analysis = BusinessImpactAnalysis()

    analysis.analyze(
        incident_id="inc-1",
        affected_users=50,
    )

    impact = analysis.get("inc-1")

    assert impact is not None
    assert impact.incident_id == "inc-1"

    assert len(analysis.list()) == 1
