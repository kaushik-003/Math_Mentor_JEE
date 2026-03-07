"""
Agent Trace Logger.
Built from Day 1 so every agent call is captured automatically.
Used to render the "Agent Trace" panel in the Streamlit sidebar.
"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceStep:
    agent_name: str
    input_summary: str
    output_summary: str
    duration_ms: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class AgentTracer:
    """Lightweight tracer that collects agent execution steps."""

    def __init__(self):
        self.steps: list[TraceStep] = []
        self._start_time: float | None = None

    def start(self, agent_name: str):
        """Call before an agent runs."""
        self._start_time = time.time()
        self._current_agent = agent_name

    def end(self, input_summary: str, output_summary: str, metadata: dict | None = None):
        """Call after an agent finishes."""
        duration = (time.time() - self._start_time) * 1000 if self._start_time else 0
        step = TraceStep(
            agent_name=self._current_agent,
            input_summary=input_summary,
            output_summary=output_summary,
            duration_ms=round(duration, 1),
            metadata=metadata or {},
        )
        self.steps.append(step)
        self._start_time = None
        return step

    def get_steps(self) -> list[TraceStep]:
        return self.steps

    def clear(self):
        self.steps = []

    def total_duration_ms(self) -> float:
        return sum(s.duration_ms for s in self.steps)