"""
Google ADK bridge.

Wraps agents built on the `google-adk` SDK so they can run
inside the OpenOps agent framework as first-class `Agent`
instances. Each ADK agent is executed through an in-memory
session with the incident context passed as the user turn.
"""

from app.infrastructure.adk.adk_agent import AdkAgent
from app.infrastructure.adk.adk_orchestrator import (
    AdkOrchestrator,
)

__all__ = [
    "AdkAgent",
    "AdkOrchestrator",
]
