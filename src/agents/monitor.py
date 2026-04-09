"""Monitor Agent - Detects anomalies in infrastructure metrics.

First agent in the Graph pipeline. Checks all services and
reports anomalies with specific metric values.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from strands import Agent, tool

if TYPE_CHECKING:
    from ..incident import Incident
    from ..infrastructure import MockInfrastructure


def create_monitor_agent(
    infra: MockInfrastructure,
    incident: Incident,
    hooks: list | None = None,
    plugins: list | None = None,
) -> Agent:
    """Creates a Monitor Agent that detects infrastructure anomalies."""

    @tool
    def get_all_metrics() -> str:
        """全サービスのメトリクスを一覧取得します。CPU、メモリ、応答時間、エラー率、接続数を確認できます。"""
        incident.add_event("monitor", "get_all_metrics", "Fetching all service metrics")
        return infra.get_all_metrics()

    @tool
    def get_service_detail(service_name: str) -> str:
        """特定サービスの詳細メトリクスを取得します。ベースラインとの比較も表示します。

        Args:
            service_name: サービス名（例: web-app, postgres-primary, redis-cache）
        """
        incident.add_event("monitor", "get_service_detail", f"Checking {service_name}")
        return infra.get_service_metrics(service_name)

    return Agent(
        name="monitor",
        system_prompt=(
            "You are an infrastructure monitoring agent. Your job is to:\n"
            "1. Check all service metrics using get_all_metrics\n"
            "2. For any service showing abnormal values, get detailed metrics\n"
            "3. Identify and summarize ALL anomalies you find\n"
            "\n"
            "Anomaly thresholds: CPU > 80%, Memory > 85%, Response time > 500ms, "
            "Error rate > 5%, or Status != healthy.\n"
            "\n"
            "Output a clear, structured summary:\n"
            "- Which services are affected and their current status\n"
            "- Specific metric values vs baseline\n"
            "- Initial severity assessment based on numbers\n"
            "\n"
            "Be thorough but concise. Always use actual numbers."
        ),
        tools=[get_all_metrics, get_service_detail],
        hooks=hooks or [],
        plugins=plugins or [],
    )
