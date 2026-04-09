"""Remediation Agent - Executes remediation actions with safety controls.

Third agent in the Graph pipeline. Receives the Triage report and
executes appropriate runbooks. Protected by Steering safety handler.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from strands import Agent, tool

if TYPE_CHECKING:
    from ..incident import Incident
    from ..infrastructure import MockInfrastructure

try:
    from strands import AgentSkills
except ImportError:
    AgentSkills = None  # type: ignore[assignment,misc]


def create_remediation_agent(
    infra: MockInfrastructure,
    incident: Incident,
    skills_path: str = "./skills/",
    hooks: list | None = None,
    plugins: list | None = None,
) -> Agent:
    """Creates a Remediation Agent with optional Skills and safety Steering."""

    @tool
    def restart_service(service_name: str) -> str:
        """サービスを再起動します。メトリクスがベースラインにリセットされます。

        Args:
            service_name: 再起動するサービス名
        """
        incident.add_event("remediation", "restart_service", f"Restarting {service_name}")
        result = infra.restart_service(service_name)
        incident.remediation_actions.append(f"restart {service_name}")
        return result

    @tool
    def scale_service(service_name: str, instances: int) -> str:
        """サービスをスケールアウトします。

        Args:
            service_name: スケールするサービス名
            instances: 目標インスタンス数（1-10）
        """
        incident.add_event("remediation", "scale_service", f"Scaling {service_name} to {instances}")
        result = infra.scale_service(service_name, instances)
        incident.remediation_actions.append(f"scale {service_name} -> {instances} instances")
        return result

    @tool
    def rollback_service(service_name: str) -> str:
        """サービスを前バージョンにロールバックします。

        Args:
            service_name: ロールバックするサービス名
        """
        incident.add_event("remediation", "rollback_service", f"Rolling back {service_name}")
        result = infra.rollback_service(service_name)
        incident.remediation_actions.append(f"rollback {service_name}")
        return result

    @tool
    def clear_cache(service_name: str) -> str:
        """キャッシュサービスのデータをクリアします。

        Args:
            service_name: キャッシュサービス名
        """
        incident.add_event("remediation", "clear_cache", f"Clearing {service_name}")
        result = infra.clear_cache(service_name)
        incident.remediation_actions.append(f"clear_cache {service_name}")
        return result

    @tool
    def check_service_status(service_name: str) -> str:
        """対象サービスの現在のステータスを確認します。修復後の検証に使います。

        Args:
            service_name: 確認するサービス名
        """
        incident.add_event("remediation", "check_status", f"Verifying {service_name}")
        return infra.check_service_status(service_name)

    all_plugins = list(plugins or [])

    # AgentSkills: load runbooks from skills/ directory if available
    if AgentSkills is not None and os.path.isdir(skills_path):
        all_plugins.append(AgentSkills(skills=skills_path))

    return Agent(
        name="remediation",
        system_prompt=(
            "You are an infrastructure remediation specialist. Based on the triage "
            "report, execute the appropriate remediation steps.\n"
            "\n"
            "Available actions:\n"
            "- restart_service: Restart a crashed or stuck service\n"
            "- scale_service: Scale out a service under heavy load (1-10 instances)\n"
            "- rollback_service: Roll back to the previous version\n"
            "- clear_cache: Clear a cache service\n"
            "- check_service_status: Verify a service after remediation\n"
            "\n"
            "Procedure:\n"
            "1. If skills are available, activate the relevant runbook first\n"
            "2. Address the ROOT CAUSE service FIRST\n"
            "3. Then address cascading effects on dependent services\n"
            "4. After each action, verify the service recovered\n"
            "5. Summarize all actions taken and their results\n"
            "\n"
            "Safety rules:\n"
            "- NEVER drop databases, delete data, or purge message queues\n"
            "- Prefer scale-out over restart when possible\n"
            "- Always verify after remediation"
        ),
        tools=[restart_service, scale_service, rollback_service, clear_cache, check_service_status],
        hooks=hooks or [],
        plugins=all_plugins,
    )
