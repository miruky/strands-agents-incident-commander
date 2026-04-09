"""Strands Agents Incident Commander - Multi-Agent Incident Response System.

4 AI agents collaborate via Graph orchestration to detect, triage,
remediate, and document infrastructure incidents autonomously.

Usage:
    python main.py                    # Default: cpu_spike scenario
    python main.py cpu_spike          # Traffic surge on web-app
    python main.py memory_leak        # Database memory leak
    python main.py cascading_failure  # Cache crash causing cascade
"""

from __future__ import annotations

import sys
import time

from strands.multiagent import GraphBuilder

from src.agents.monitor import create_monitor_agent
from src.agents.postmortem import create_postmortem_agent
from src.agents.remediation import create_remediation_agent
from src.agents.triage import create_triage_agent
from src.incident import Incident
from src.infrastructure import MockInfrastructure
from src.plugins.audit_trail import AuditTrailPlugin
from src.plugins.cost_tracker import CostTrackerHook
from src.scenarios import ALL_SCENARIOS
from src.steering.safety import create_safety_handler


def run_incident_response(scenario_key: str = "cpu_spike") -> None:
    """Runs the full incident response pipeline for a given scenario."""

    scenario = ALL_SCENARIOS.get(scenario_key)
    if not scenario:
        print(f"Unknown scenario: '{scenario_key}'")
        print(f"Available scenarios: {', '.join(ALL_SCENARIOS.keys())}")
        sys.exit(1)

    print("=" * 60)
    print("  Strands Agents Incident Commander")
    print("=" * 60)
    print(f"\n  Scenario:    {scenario['name']}")
    print(f"  Description: {scenario['description']}")
    print()

    # ------------------------------------------------------------------ #
    #  1. Initialize shared objects
    # ------------------------------------------------------------------ #
    infra = MockInfrastructure()
    incident = Incident(title=scenario["name"])

    # Hooks & Plugins shared across all agents
    audit = AuditTrailPlugin(incident)
    cost_tracker = CostTrackerHook()
    safety = create_safety_handler()

    # ------------------------------------------------------------------ #
    #  2. Inject the failure
    # ------------------------------------------------------------------ #
    print("[*] Injecting failure scenario...")
    infra.inject_failure(scenario)
    incident.add_event("system", "failure_injected", scenario["name"])
    print("[*] Failure injected.\n")

    # ------------------------------------------------------------------ #
    #  3. Create agents
    # ------------------------------------------------------------------ #
    monitor = create_monitor_agent(
        infra, incident,
        hooks=[cost_tracker], plugins=[audit],
    )
    triage = create_triage_agent(
        infra, incident,
        hooks=[cost_tracker], plugins=[audit],
    )
    remediation = create_remediation_agent(
        infra, incident,
        hooks=[cost_tracker], plugins=[audit, safety],
    )
    postmortem = create_postmortem_agent(
        incident,
        hooks=[cost_tracker], plugins=[audit],
    )

    # ------------------------------------------------------------------ #
    #  4. Build multi-agent graph
    #     Monitor → Triage → Remediation → Postmortem
    # ------------------------------------------------------------------ #
    builder = GraphBuilder()
    builder.add_node(monitor, "monitor")
    builder.add_node(triage, "triage")
    builder.add_node(remediation, "remediation")
    builder.add_node(postmortem, "postmortem")

    builder.add_edge("monitor", "triage")
    builder.add_edge("triage", "remediation")
    builder.add_edge("remediation", "postmortem")

    builder.set_entry_point("monitor")
    builder.set_execution_timeout(600)

    graph = builder.build()

    # ------------------------------------------------------------------ #
    #  5. Execute the pipeline
    # ------------------------------------------------------------------ #
    task = (
        f"INFRASTRUCTURE ALERT: {scenario['description']}\n"
        f"Investigate the current infrastructure state, determine the root cause, "
        f"execute appropriate remediation, and generate a postmortem report."
    )

    print("=" * 60)
    print("  Executing: Monitor -> Triage -> Remediation -> Postmortem")
    print("=" * 60)
    print()

    start_time = time.time()
    result = graph(task)
    elapsed = time.time() - start_time

    # ------------------------------------------------------------------ #
    #  6. Print results
    # ------------------------------------------------------------------ #
    print()
    print("=" * 60)
    print("  Pipeline Complete")
    print("=" * 60)
    print(f"  Status:          {result.status}")
    print(f"  Execution Time:  {elapsed:.1f}s")
    print(f"  Node Order:      {' -> '.join(n.node_id for n in result.execution_order)}")
    print(f"  Total Nodes:     {result.total_nodes}")
    print(f"  Completed Nodes: {result.completed_nodes}")

    if result.execution_time:
        print(f"  Graph Time:      {result.execution_time}ms")

    # Cost summary
    cost = cost_tracker.get_summary()
    print(f"\n  Model Calls: {cost['model_calls']}")
    print(f"  Tool Calls:  {cost['tool_calls']}")

    # Token usage from graph result
    if hasattr(result, "accumulated_usage") and result.accumulated_usage:
        usage = result.accumulated_usage
        input_t = usage.get("inputTokens", 0) if isinstance(usage, dict) else getattr(usage, "inputTokens", 0)
        output_t = usage.get("outputTokens", 0) if isinstance(usage, dict) else getattr(usage, "outputTokens", 0)
        if input_t or output_t:
            cost_usd = (input_t * 3.0 + output_t * 15.0) / 1_000_000
            print(f"  Input Tokens:    {input_t:,}")
            print(f"  Output Tokens:   {output_t:,}")
            print(f"  Estimated Cost:  ${cost_usd:.4f}")

    # Incident summary
    print(f"\n{'=' * 60}")
    print("  Incident Summary")
    print("=" * 60)
    print(incident.to_summary())

    # Postmortem output
    if "postmortem" in result.results and result.results["postmortem"].result:
        print(f"\n{'=' * 60}")
        print("  Postmortem Report (generated by AI)")
        print("=" * 60)
        print(str(result.results["postmortem"].result))


if __name__ == "__main__":
    scenario_key = sys.argv[1] if len(sys.argv) > 1 else "cpu_spike"
    run_incident_response(scenario_key)
