from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock


@dataclass
class ServiceDependency:
    """
    A dependency relationship between two services.
    """

    dependent: str

    dependency: str

    critical: bool = False

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )


@dataclass
class ImpactAnalysis:
    """
    Result of analyzing the impact of a service failure.
    """

    service: str

    directly_affected: list[str] = field(
        default_factory=list
    )

    transitively_affected: list[str] = field(
        default_factory=list
    )

    critical_dependencies: list[str] = field(
        default_factory=list
    )

    analyzed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class DependencyIntelligence:
    """
    Maps service dependencies and analyzes failure impact.

    - Registers dependency relationships between services.
    - Computes directly and transitively affected services
      when a service fails.
    """

    def __init__(self) -> None:

        self._dependencies: list[ServiceDependency] = []

        self._lock = Lock()

    def register_dependency(
        self,
        *,
        dependent: str,
        dependency: str,
        critical: bool = False,
    ) -> ServiceDependency:

        entry = ServiceDependency(
            dependent=dependent,
            dependency=dependency,
            critical=critical,
        )

        with self._lock:
            self._dependencies.append(entry)

        return entry

    def dependencies_of(
        self,
        service: str,
    ) -> list[ServiceDependency]:
        """
        Returns the services that `service` depends on.
        """

        with self._lock:

            return [
                dep
                for dep in self._dependencies
                if dep.dependent == service
            ]

    def dependents_of(
        self,
        service: str,
    ) -> list[ServiceDependency]:
        """
        Returns the services that depend on `service`.
        """

        with self._lock:

            return [
                dep
                for dep in self._dependencies
                if dep.dependency == service
            ]

    def impact_analysis(
        self,
        service: str,
    ) -> ImpactAnalysis:
        """
        Computes the blast radius of a service failure.
        """

        dependents = self.dependents_of(service)

        directly = [
            dep.dependent
            for dep in dependents
        ]

        critical = [
            dep.dependent
            for dep in dependents
            if dep.critical
        ]

        transitively = self._transitive_impact(
            service,
            set(directly),
        )

        return ImpactAnalysis(
            service=service,
            directly_affected=directly,
            transitively_affected=transitively,
            critical_dependencies=critical,
        )

    def is_affected(
        self,
        service: str,
        failed: str,
    ) -> bool:
        """
        True when `service` is affected by `failed`.
        """

        analysis = self.impact_analysis(failed)

        return (
            service in analysis.directly_affected
            or service in analysis.transitively_affected
        )

    def list(self) -> list[ServiceDependency]:

        with self._lock:
            return list(self._dependencies)

    def clear(self) -> None:

        with self._lock:
            self._dependencies.clear()

    # ==========================================================
    # Helpers
    # ==========================================================

    def _transitive_impact(
        self,
        failed: str,
        directly: set[str],
    ) -> list[str]:
        """
        Breadth-first traversal over dependents to find all
        transitively affected services (excluding the directly
        affected ones).
        """

        visited: set[str] = set()

        frontier = list(directly)

        while frontier:

            current = frontier.pop()

            for dep in self.dependents_of(current):

                if (
                    dep.dependent not in visited
                    and dep.dependent not in directly
                ):

                    visited.add(dep.dependent)
                    frontier.append(dep.dependent)

        if failed in visited:
            visited.discard(failed)

        return list(visited)
