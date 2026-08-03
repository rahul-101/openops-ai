from app.infrastructure.governance.audit_log import (
    AuditLogService,
)


def test_record_entry():

    audit = AuditLogService()

    entry = audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
        incident_id="inc-1",
        agent="root-cause-agent",
        model="gpt-4o",
    )

    assert entry.id
    assert entry.user == "alice"
    assert entry.action == "incident.analyze"
    assert entry.decision == "auto_executed"
    assert entry.incident_id == "inc-1"
    assert entry.agent == "root-cause-agent"
    assert entry.model == "gpt-4o"
    assert entry.timestamp is not None


def test_record_with_metadata():

    audit = AuditLogService()

    entry = audit.record(
        user="bob",
        action="tool.kubernetes.restart",
        decision="approval_required",
        request_id="req-42",
    )

    assert entry.metadata["request_id"] == "req-42"


def test_list_all_entries():

    audit = AuditLogService()

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
    )

    audit.record(
        user="bob",
        action="tool.aws.delete",
        decision="blocked",
    )

    assert len(audit.list()) == 2


def test_list_filter_by_user():

    audit = AuditLogService()

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
    )

    audit.record(
        user="bob",
        action="tool.aws.delete",
        decision="blocked",
    )

    entries = audit.list(user="alice")

    assert len(entries) == 1
    assert entries[0].user == "alice"


def test_list_filter_by_action_and_decision():

    audit = AuditLogService()

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
        incident_id="inc-1",
    )

    audit.record(
        user="bob",
        action="incident.analyze",
        decision="approval_required",
        incident_id="inc-1",
    )

    entries = audit.list(
        action="incident.analyze",
        decision="approval_required",
    )

    assert len(entries) == 1
    assert entries[0].user == "bob"


def test_list_filter_by_incident_id():

    audit = AuditLogService()

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
        incident_id="inc-1",
    )

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
        incident_id="inc-2",
    )

    entries = audit.list(incident_id="inc-1")

    assert len(entries) == 1
    assert entries[0].incident_id == "inc-1"


def test_list_respects_limit():

    audit = AuditLogService()

    for i in range(5):
        audit.record(
            user="alice",
            action=f"action-{i}",
            decision="auto_executed",
        )

    entries = audit.list(limit=2)

    assert len(entries) == 2


def test_clear():

    audit = AuditLogService()

    audit.record(
        user="alice",
        action="incident.analyze",
        decision="auto_executed",
    )

    audit.clear()

    assert audit.list() == []
