import pytest

from app.infrastructure.governance.exceptions import (
    AuthorizationError,
)
from app.infrastructure.governance.models import Permission
from app.infrastructure.governance.rbac import RbacService


@pytest.fixture
def rbac() -> RbacService:

    service = RbacService()

    service.register_user(
        "alice",
        roles=["admin"],
    )

    service.register_user(
        "bob",
        roles=["operator"],
    )

    service.register_user(
        "carol",
        roles=["viewer"],
    )

    return service


def test_register_user_and_roles(rbac):

    user = rbac.register_user(
        "dave",
        roles=["analyst"],
    )

    assert user.username == "dave"
    assert "analyst" in user.roles
    assert rbac.roles_for("dave") == ["analyst"]


def test_assign_role(rbac):

    rbac.assign_role("carol", "analyst")

    assert "analyst" in rbac.roles_for("carol")


def test_admin_has_all_permissions(rbac):

    for permission in Permission:
        assert rbac.has_permission("alice", permission) is True


def test_operator_permissions(rbac):

    assert rbac.has_permission(
        "bob", Permission.TOOL_EXECUTE
    ) is True

    assert rbac.has_permission(
        "bob", Permission.ADMIN
    ) is False


def test_viewer_restricted(rbac):

    assert rbac.has_permission(
        "carol", Permission.INCIDENT_READ
    ) is True

    assert rbac.has_permission(
        "carol", Permission.TOOL_EXECUTE
    ) is False


def test_unknown_user_has_no_permissions(rbac):

    assert rbac.has_permission(
        "ghost", Permission.INCIDENT_READ
    ) is False


def test_authorize_passes_when_allowed(rbac):

    rbac.authorize("bob", Permission.INCIDENT_WRITE)


def test_authorize_raises_when_denied(rbac):

    with pytest.raises(AuthorizationError):
        rbac.authorize(
            "carol",
            Permission.AI_EXECUTE,
        )


def test_list_users(rbac):

    users = rbac.list_users()

    assert sorted(u.username for u in users) == [
        "alice",
        "bob",
        "carol",
    ]
