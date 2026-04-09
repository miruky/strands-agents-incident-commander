"""Postmortem Agent - Generates structured incident reports.

Final agent in the Graph pipeline. Receives all previous output
and generates a comprehensive postmortem document.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from strands import Agent, tool

if TYPE_CHECKING:
    from ..incident import Incident


def create_postmortem_agent(
    incident: Incident,
    hooks: list | None = None,
    plugins: list | None = None,
) -> Agent:
    """Creates a Postmortem Agent that generates incident reports."""

    @tool
    def get_incident_timeline() -> str:
        """インシデントの全タイムラインを取得します。全エージェントの操作記録が含まれます。"""
        return incident.get_timeline_text()

    @tool
    def get_incident_summary() -> str:
        """インシデントのサマリー（ID、重大度、影響範囲、修復アクション等）を取得します。"""
        return incident.to_summary()

    return Agent(
        name="postmortem",
        system_prompt=(
            "You are an incident postmortem analyst. Generate a structured postmortem "
            "report based on all the information from previous agents and the incident "
            "timeline.\n"
            "\n"
            "Use the tools to retrieve the full timeline and incident summary.\n"
            "\n"
            "Report structure (use these exact section headers):\n"
            "1. INCIDENT SUMMARY - One-paragraph overview\n"
            "2. TIMELINE - Key events in chronological order\n"
            "3. ROOT CAUSE ANALYSIS - What failed and why\n"
            "4. IMPACT - Services affected, duration, user impact\n"
            "5. REMEDIATION - Actions taken and their results\n"
            "6. LESSONS LEARNED - What could be improved\n"
            "7. ACTION ITEMS - Specific follow-up tasks\n"
            "\n"
            "Be factual. Reference specific numbers and timestamps from the data."
        ),
        tools=[get_incident_timeline, get_incident_summary],
        hooks=hooks or [],
        plugins=plugins or [],
    )
