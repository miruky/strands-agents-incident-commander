"""Incident data model for tracking events across agents."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IncidentEvent:
    """A single event in the incident timeline."""

    timestamp: str
    agent: str
    action: str
    detail: str


@dataclass
class Incident:
    """Tracks an incident across the entire response pipeline.

    Thread-safe: all mutations go through a lock so hooks from
    concurrent tool executions don't corrupt state.
    """

    id: str = field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    title: str = ""
    severity: str = ""
    status: str = "detected"
    affected_services: list[str] = field(default_factory=list)
    root_cause: str = ""
    timeline: list[IncidentEvent] = field(default_factory=list)
    remediation_actions: list[str] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add_event(self, agent: str, action: str, detail: str) -> None:
        """Thread-safe event addition to the timeline."""
        with self._lock:
            self.timeline.append(
                IncidentEvent(
                    timestamp=datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    agent=agent,
                    action=action,
                    detail=detail[:200],
                )
            )

    def to_summary(self) -> str:
        """Returns a formatted summary of the incident."""
        lines = [
            f"Incident ID:       {self.id}",
            f"Title:             {self.title}",
            f"Severity:          {self.severity or 'TBD'}",
            f"Status:            {self.status}",
            f"Affected Services: {', '.join(self.affected_services) or 'TBD'}",
            f"Root Cause:        {self.root_cause or 'TBD'}",
            "",
            f"Timeline ({len(self.timeline)} events):",
        ]
        for e in self.timeline:
            lines.append(f"  [{e.timestamp}] [{e.agent}] {e.action}: {e.detail}")
        if self.remediation_actions:
            lines.append("")
            lines.append("Remediation Actions:")
            for a in self.remediation_actions:
                lines.append(f"  - {a}")
        return "\n".join(lines)

    def get_timeline_text(self) -> str:
        """Returns compact timeline text for agents to consume."""
        if not self.timeline:
            return "No events recorded yet."
        lines = []
        for e in self.timeline:
            lines.append(f"[{e.timestamp}] [{e.agent}] {e.action}: {e.detail}")
        return "\n".join(lines)
