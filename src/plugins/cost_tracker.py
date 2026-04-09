"""CostTrackerHook - Tracks model and tool invocations across all agents.

Demonstrates the HookProvider pattern with register_hooks().
Shared across agents to aggregate metrics for the entire pipeline.
"""

from __future__ import annotations

from threading import Lock

from strands.hooks import (
    AfterModelCallEvent,
    AfterToolCallEvent,
    HookProvider,
    HookRegistry,
)


class CostTrackerHook(HookProvider):
    """Counts model calls and tool calls across all agents in the pipeline."""

    def __init__(self) -> None:
        self.model_calls = 0
        self.tool_calls = 0
        self._lock = Lock()

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterModelCallEvent, self._on_model_call)
        registry.add_callback(AfterToolCallEvent, self._on_tool_call)

    def _on_model_call(self, event: AfterModelCallEvent) -> None:  # noqa: ARG002
        with self._lock:
            self.model_calls += 1

    def _on_tool_call(self, event: AfterToolCallEvent) -> None:  # noqa: ARG002
        with self._lock:
            self.tool_calls += 1

    def get_summary(self) -> dict[str, int]:
        return {
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,
        }
