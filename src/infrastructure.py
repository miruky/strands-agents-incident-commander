"""Mock infrastructure for the incident response simulator.

Simulates a microservice architecture with 6 services.
Each service has metrics (CPU, memory, response time, etc.) and dependency relationships.
Supports failure injection and remediation actions.
"""

from __future__ import annotations

import copy
import threading
from dataclasses import dataclass, field


@dataclass
class ServiceMetrics:
    """Metrics for a single service."""

    cpu_percent: float = 25.0
    memory_percent: float = 40.0
    response_time_ms: float = 50.0
    error_rate_percent: float = 0.1
    active_connections: int = 100


@dataclass
class Service:
    """A single service in the mock infrastructure."""

    name: str
    service_type: str
    status: str = "healthy"
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)
    dependencies: list[str] = field(default_factory=list)
    version: str = "v2.1.0"
    previous_version: str = "v2.0.0"


class MockInfrastructure:
    """Simulates a cloud infrastructure with multiple services.

    Services:
        api-gateway  → web-app → postgres-primary, redis-cache, rabbitmq
        worker       → rabbitmq, postgres-primary
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.services = self._create_default_services()
        self._baseline: dict[str, ServiceMetrics] = {}
        self._save_baseline()

    def _create_default_services(self) -> dict[str, Service]:
        return {
            "api-gateway": Service(
                name="api-gateway",
                service_type="gateway",
                metrics=ServiceMetrics(
                    cpu_percent=30.0, memory_percent=45.0, response_time_ms=15.0,
                    error_rate_percent=0.05, active_connections=800,
                ),
                dependencies=["web-app"],
            ),
            "web-app": Service(
                name="web-app",
                service_type="web",
                metrics=ServiceMetrics(
                    cpu_percent=35.0, memory_percent=55.0, response_time_ms=120.0,
                    error_rate_percent=0.1, active_connections=450,
                ),
                dependencies=["postgres-primary", "redis-cache", "rabbitmq"],
            ),
            "postgres-primary": Service(
                name="postgres-primary",
                service_type="database",
                metrics=ServiceMetrics(
                    cpu_percent=40.0, memory_percent=60.0, response_time_ms=5.0,
                    error_rate_percent=0.0, active_connections=100,
                ),
                dependencies=[],
            ),
            "redis-cache": Service(
                name="redis-cache",
                service_type="cache",
                metrics=ServiceMetrics(
                    cpu_percent=15.0, memory_percent=45.0, response_time_ms=1.0,
                    error_rate_percent=0.0, active_connections=200,
                ),
                dependencies=[],
            ),
            "rabbitmq": Service(
                name="rabbitmq",
                service_type="queue",
                metrics=ServiceMetrics(
                    cpu_percent=20.0, memory_percent=30.0, response_time_ms=2.0,
                    error_rate_percent=0.0, active_connections=50,
                ),
                dependencies=[],
            ),
            "worker": Service(
                name="worker",
                service_type="worker",
                metrics=ServiceMetrics(
                    cpu_percent=55.0, memory_percent=50.0, response_time_ms=0.0,
                    error_rate_percent=0.2, active_connections=0,
                ),
                dependencies=["rabbitmq", "postgres-primary"],
            ),
        }

    def _save_baseline(self) -> None:
        for name, svc in self.services.items():
            self._baseline[name] = copy.deepcopy(svc.metrics)

    # ------------------------------------------------------------------ #
    #  Read-only operations (used by Monitor / Triage agents)
    # ------------------------------------------------------------------ #

    def get_all_metrics(self) -> str:
        """Returns formatted metrics for all services."""
        with self._lock:
            lines = ["=== Infrastructure Status ===", ""]
            for name, svc in self.services.items():
                m = svc.metrics
                tag = {"healthy": "OK", "degraded": "WARN", "critical": "CRIT", "down": "DOWN"}.get(
                    svc.status, "???"
                )
                lines.append(
                    f"[{tag}] {name} ({svc.service_type})\n"
                    f"  CPU: {m.cpu_percent:.1f}% | Memory: {m.memory_percent:.1f}% | "
                    f"Response: {m.response_time_ms:.0f}ms | Errors: {m.error_rate_percent:.2f}% | "
                    f"Connections: {m.active_connections}"
                )
            return "\n".join(lines)

    def get_service_metrics(self, service_name: str) -> str:
        """Returns detailed metrics for a specific service including baseline comparison."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Service '{service_name}' not found. Available: {', '.join(self.services.keys())}"
            m = svc.metrics
            b = self._baseline.get(service_name, m)
            lines = [
                f"=== {svc.name} ({svc.service_type}) ===",
                f"Status:  {svc.status}",
                f"Version: {svc.version}",
                "",
                "Metrics (current vs baseline):",
                f"  CPU:         {m.cpu_percent:6.1f}%   (baseline {b.cpu_percent:.1f}%)",
                f"  Memory:      {m.memory_percent:6.1f}%   (baseline {b.memory_percent:.1f}%)",
                f"  Response:    {m.response_time_ms:6.0f}ms  (baseline {b.response_time_ms:.0f}ms)",
                f"  Error Rate:  {m.error_rate_percent:6.2f}%   (baseline {b.error_rate_percent:.2f}%)",
                f"  Connections: {m.active_connections:6d}    (baseline {b.active_connections})",
                "",
                f"Dependencies: {', '.join(svc.dependencies) if svc.dependencies else 'none'}",
            ]
            return "\n".join(lines)

    def get_service_dependencies(self, service_name: str) -> str:
        """Returns dependency graph for a service (upstream + downstream)."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Service '{service_name}' not found."
            lines = [f"=== Dependency Graph for {svc.name} ===", ""]

            # Downstream (this service depends on)
            if svc.dependencies:
                lines.append("Depends on:")
                for dep_name in svc.dependencies:
                    dep = self.services.get(dep_name)
                    if dep:
                        lines.append(f"  -> {dep.name} ({dep.service_type}): {dep.status}")
            else:
                lines.append("Depends on: nothing (leaf service)")

            # Upstream (services that depend on this)
            dependents = [s.name for s in self.services.values() if service_name in s.dependencies]
            lines.append("")
            if dependents:
                lines.append(f"Depended on by: {', '.join(dependents)}")
            else:
                lines.append("Depended on by: nothing (root service)")
            return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Write operations (used by Remediation agent)
    # ------------------------------------------------------------------ #

    def inject_failure(self, scenario: dict) -> None:
        """Injects a failure scenario by mutating service metrics and status."""
        with self._lock:
            for service_name, updates in scenario.get("changes", {}).items():
                svc = self.services.get(service_name)
                if not svc:
                    continue
                for key, value in updates.items():
                    if key == "status":
                        svc.status = value
                    elif hasattr(svc.metrics, key):
                        setattr(svc.metrics, key, value)

    def restart_service(self, service_name: str) -> str:
        """Restarts a service, resetting metrics to baseline."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Error: Service '{service_name}' not found."
            baseline = self._baseline.get(service_name)
            if baseline:
                svc.metrics = copy.deepcopy(baseline)
            svc.status = "healthy"
            return (
                f"Service '{service_name}' restarted successfully. "
                f"Status: healthy. Metrics reset to baseline."
            )

    def scale_service(self, service_name: str, instances: int) -> str:
        """Scales a service by reducing load proportionally to instance count."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Error: Service '{service_name}' not found."
            if not 1 <= instances <= 10:
                return "Error: Instance count must be between 1 and 10."
            factor = 1.0 / instances
            svc.metrics.cpu_percent = max(5.0, svc.metrics.cpu_percent * factor)
            svc.metrics.response_time_ms = max(1.0, svc.metrics.response_time_ms * factor)
            svc.metrics.error_rate_percent = max(0.0, svc.metrics.error_rate_percent * factor)
            if svc.status in ("critical", "degraded"):
                svc.status = "healthy" if svc.metrics.cpu_percent < 80 else "degraded"
            return (
                f"Service '{service_name}' scaled to {instances} instances. "
                f"CPU: {svc.metrics.cpu_percent:.1f}%, Response: {svc.metrics.response_time_ms:.0f}ms, "
                f"Status: {svc.status}"
            )

    def rollback_service(self, service_name: str) -> str:
        """Rolls back a service to its previous version and resets metrics."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Error: Service '{service_name}' not found."
            old_version = svc.version
            svc.version = svc.previous_version
            svc.previous_version = old_version
            baseline = self._baseline.get(service_name)
            if baseline:
                svc.metrics = copy.deepcopy(baseline)
            svc.status = "healthy"
            return f"Service '{service_name}' rolled back from {old_version} to {svc.version}. Status: healthy."

    def clear_cache(self, service_name: str) -> str:
        """Clears a cache service."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Error: Service '{service_name}' not found."
            if svc.service_type != "cache":
                return f"Error: '{service_name}' is a {svc.service_type}, not a cache."
            svc.metrics.memory_percent = 10.0
            svc.metrics.response_time_ms = 0.5
            svc.status = "healthy"
            return f"Cache '{service_name}' cleared. Memory: 10.0%, Status: healthy."

    def check_service_status(self, service_name: str) -> str:
        """Quick health check returning current status and key metrics."""
        with self._lock:
            svc = self.services.get(service_name)
            if not svc:
                return f"Service '{service_name}' not found."
            m = svc.metrics
            return (
                f"{svc.name}: {svc.status} "
                f"(CPU: {m.cpu_percent:.1f}%, Memory: {m.memory_percent:.1f}%, "
                f"Errors: {m.error_rate_percent:.2f}%, Response: {m.response_time_ms:.0f}ms)"
            )
