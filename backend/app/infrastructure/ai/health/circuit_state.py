from enum import Enum


class CircuitState(str, Enum):
    """
    Circuit Breaker state.

    CLOSED
        Provider is healthy.

    OPEN
        Provider is blocked due to repeated failures.

    HALF_OPEN
        Provider is being tested after cooldown.
    """

    CLOSED = "closed"

    OPEN = "open"

    HALF_OPEN = "half_open"