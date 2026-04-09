"""Triage Agent - Classifies incident severity and identifies root cause.

Second agent in the Graph pipeline. Receives the Monitor's anomaly
report and performs dependency analysis to determine blast radius.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from strands import Agent, tool

if TYPE_CHECKING:
    from ..incident import Incident
    from ..infrastructure import MockInfrastructure


def create_triage_agent(
    infra: MockInfrastructure,
    incident: Incident,
    hooks: list | None = None,
    plugins: list | None = None,
) -> Agent:
    """Creates a Triage Agent that classifies severity and identifies root cause."""

    @tool
    def get_service_dependencies(service_name: str) -> str:
        """サービスの依存関係グラフを取得します。上流・下流のサービス関係を表示します。

        Args:
            service_name: サービス名
        """
        incident.add_event("triage", "get_dependencies", f"Analyzing dependencies for {service_name}")
        return infra.get_service_dependencies(service_name)

    @tool
    def get_service_status(service_name: str) -> str:
        """サービスの現在のステータスと詳細メトリクスを取得します。

        Args:
            service_name: サービス名
        """
        incident.add_event("triage", "get_service_status", f"Checking {service_name}")
        return infra.get_service_metrics(service_name)

    return Agent(
        name="triage",
        system_prompt=(
            "You are an incident triage specialist. Based on the monitoring report "
            "you received, your job is to:\n"
            "1. Analyze service dependencies to understand the blast radius\n"
            "2. Identify the ROOT CAUSE (the originating service/failure)\n"
            "3. Classify severity using this scale:\n"
            "   - P1 (Critical): Multiple services down, user-facing impact > 50%\n"
            "   - P2 (High): Single critical service degraded, significant user impact\n"
            "   - P3 (Medium): Non-critical service degraded, limited user impact\n"
            "   - P4 (Low): Minor anomaly, no user impact\n"
            "\n"
            "Use the dependency tools to trace the failure propagation path.\n"
            "\n"
            "Output a structured triage report:\n"
            "- SEVERITY: P1/P2/P3/P4 with justification\n"
            "- ROOT CAUSE: Originating service and specific issue\n"
            "- BLAST RADIUS: All affected services and how\n"
            "- RECOMMENDED ACTIONS: Specific remediation steps in priority order"
        ),
        tools=[get_service_dependencies, get_service_status],
        hooks=hooks or [],
        plugins=plugins or [],
    )
