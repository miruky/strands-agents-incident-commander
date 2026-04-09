"""Predefined failure scenarios for the incident response simulator.

Each scenario defines which services are affected and how their
metrics/status change when the failure is injected.
"""

CPU_SPIKE = {
    "name": "CPU Spike - Traffic Surge",
    "description": (
        "The web-app server is experiencing a sudden CPU spike to 96% due to an "
        "unexpected traffic surge. Response times have increased 30x and error rates "
        "have spiked. The api-gateway is also showing degradation."
    ),
    "changes": {
        "web-app": {
            "cpu_percent": 96.0,
            "memory_percent": 82.0,
            "response_time_ms": 3500.0,
            "error_rate_percent": 15.0,
            "active_connections": 2000,
            "status": "critical",
        },
        "api-gateway": {
            "response_time_ms": 4000.0,
            "error_rate_percent": 12.0,
            "active_connections": 2500,
            "status": "degraded",
        },
    },
}

MEMORY_LEAK = {
    "name": "Memory Leak - Database",
    "description": (
        "The postgres-primary database is showing memory usage at 95% and growing, "
        "indicating a memory leak. Query response times have increased 20x. "
        "The web-app is experiencing stalled connections as a result."
    ),
    "changes": {
        "postgres-primary": {
            "cpu_percent": 78.0,
            "memory_percent": 95.0,
            "response_time_ms": 100.0,
            "error_rate_percent": 8.0,
            "active_connections": 95,
            "status": "critical",
        },
        "web-app": {
            "response_time_ms": 800.0,
            "error_rate_percent": 5.0,
            "status": "degraded",
        },
    },
}

CASCADING_FAILURE = {
    "name": "Cascading Failure - Cache Down",
    "description": (
        "The redis-cache has crashed completely. All requests are hitting the database "
        "directly, causing a cascade: postgres-primary is overloaded, web-app response "
        "times are through the roof, and the api-gateway is timing out."
    ),
    "changes": {
        "redis-cache": {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "response_time_ms": 0.0,
            "error_rate_percent": 100.0,
            "active_connections": 0,
            "status": "down",
        },
        "postgres-primary": {
            "cpu_percent": 92.0,
            "memory_percent": 85.0,
            "response_time_ms": 500.0,
            "error_rate_percent": 10.0,
            "active_connections": 500,
            "status": "critical",
        },
        "web-app": {
            "cpu_percent": 80.0,
            "memory_percent": 75.0,
            "response_time_ms": 5000.0,
            "error_rate_percent": 25.0,
            "active_connections": 1800,
            "status": "critical",
        },
        "api-gateway": {
            "response_time_ms": 6000.0,
            "error_rate_percent": 20.0,
            "active_connections": 3000,
            "status": "critical",
        },
    },
}

ALL_SCENARIOS = {
    "cpu_spike": CPU_SPIKE,
    "memory_leak": MEMORY_LEAK,
    "cascading_failure": CASCADING_FAILURE,
}
