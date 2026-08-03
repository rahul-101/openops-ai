from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from app.infrastructure.governance.exceptions import (
    AuthorizationError,
)
from app.infrastructure.governance.models import Permission


@dataclass
class User:
    """
    A governed user with assigned roles.
    """

    username: str

    roles: list[str] = field(default_factory=list)

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


DEFAULT_ROLE_PERMISSIONS = {
    "admin": set(Permission),
    "operator": {
        Permission.INCIDENT_READ,
        Permission.INCIDENT_WRITE,
        Permission.AI_EXECUTE,
        Permission.TOOL_EXECUTE,
        Permission.APPROVAL_APPROVE,
        Permission.GOVERNANCE_READ,
    },
    "analyst": {
        Permission.INCIDENT_READ,
        Permission.INCIDENT_WRITE,
        Permission.AI_EXECUTE,
        Permission.GOVERNANCE_READ,
    },
    "viewer": {
        Permission.INCIDENT_READ,
        Permission.GOVERNANCE_READ,
    },
}


class RbacService:
    """
    Role-based access control.

    Manages users, roles and permissions, and performs
    authorization checks.
    """

    def __init__(
        self,
        role_permissions: dict[str, set[Permission]] | None = None,
    ) -> None:

        self._users: dict[str, User] = {}

        self._role_permissions = (
            role_permissions
            or DEFAULT_ROLE_PERMISSIONS
        )

        self._lock = Lock()

    # ==========================================================
    # Users & Roles
    # ==========================================================

    def register_user(
        self,
        username: str,
        roles: list[str] | None = None,
    ) -> User:

        with self._lock:

            user = self._users.get(username)

            if user is None:
                user = User(
                    username=username,
                    roles=list(roles or []),
                )
                self._users[username] = user

            else:
                for role in roles or []:
                    if role not in user.roles:
                        user.roles.append(role)

            return user

    def assign_role(
        self,
        username: str,
        role: str,
    ) -> User:

        with self._lock:

            user = self._users.get(username)

            if user is None:
                user = User(
                    username=username,
                )
                self._users[username] = user

            if role not in user.roles:
                user.roles.append(role)

            return user

    def roles_for(
        self,
        username: str,
    ) -> list[str]:

        with self._lock:

            user = self._users.get(username)

            if user is None:
                return []

            return list(user.roles)

    def list_users(self) -> list[User]:

        with self._lock:
            return list(self._users.values())

    # ==========================================================
    # Authorization
    # ==========================================================

    def permissions_for(
        self,
        username: str,
    ) -> set[Permission]:

        permissions: set[Permission] = set()

        for role in self.roles_for(username):

            role_permissions = (
                self._role_permissions.get(role)
            )

            if role_permissions:
                permissions.update(role_permissions)

        return permissions

    def has_permission(
        self,
        username: str,
        permission: Permission,
    ) -> bool:

        return permission in self.permissions_for(username)

    def authorize(
        self,
        username: str,
        permission: Permission,
    ) -> None:
        """
        Raises AuthorizationError when the user lacks the
        permission.
        """

        if not self.has_permission(username, permission):
            raise AuthorizationError(
                f"User '{username}' is not authorized for "
                f"'{permission.value}'."
            )
