"""Remediation Safety Handler - Steering plugin for safe remediation actions.

Demonstrates the Steering pattern using LLMSteeringHandler.
Evaluates remediation tool calls before execution and blocks unsafe actions.
"""

from __future__ import annotations

from strands.vended_plugins.steering import LLMSteeringHandler


def create_safety_handler() -> LLMSteeringHandler:
    """Creates a Steering handler that validates remediation actions for safety.

    The handler intercepts tool calls on the Remediation agent and uses a
    secondary LLM evaluation to decide whether the action is safe to proceed.
    """
    return LLMSteeringHandler(
        system_prompt=(
            "You are a safety reviewer for infrastructure remediation actions.\n"
            "\n"
            "Before ANY remediation tool is executed, verify:\n"
            "1. The action targets a service that was identified as affected\n"
            "2. The action is proportionate to the incident severity\n"
            "3. The action will NOT cause data loss or corruption\n"
            "4. The action is reversible\n"
            "\n"
            "BLOCK any action that:\n"
            "- Targets a service NOT identified in the triage report\n"
            "- Could cause data loss (dropping tables, deleting files, purging queues)\n"
            "- Is disproportionately aggressive for a low-severity issue\n"
            "\n"
            "If the action is safe, allow it to proceed.\n"
            "If unsafe, explain why and suggest a safer alternative."
        ),
    )
