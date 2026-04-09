"""AuditTrailPlugin - Logs every tool call to the incident timeline.

Demonstrates the Plugin pattern: @hook decorators auto-register
callbacks when the plugin is attached to an Agent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent
from strands.plugins import Plugin, hook

if TYPE_CHECKING:
    from ..incident import Incident


class AuditTrailPlugin(Plugin):
    """Records all tool invocations in the shared Incident timeline."""

    name = "audit-trail"

    def __init__(self, incident: Incident) -> None:
        self.incident = incident

    @hook
    def log_before_tool(self, event: BeforeToolCallEvent) -> None:
        tool_name = event.tool_use["name"]
        tool_input = str(event.tool_use.get("input", ""))[:100]
        self.incident.add_event(
            agent="audit",
            action=f"-> {tool_name}",
            detail=tool_input,
        )

    @hook
    def log_after_tool(self, event: AfterToolCallEvent) -> None:
        tool_name = event.tool_use["name"]
        status = "error" if event.exception else "ok"
        if event.cancel_message:
            status = "cancelled"
        self.incident.add_event(
            agent="audit",
            action=f"<- {tool_name}",
            detail=f"status={status}",
        )
