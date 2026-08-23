from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Protocol


class Risk(str, Enum):
    NONE = "none"
    PREMIUM_CURRENCY = "premium_currency"
    PVP = "pvp"
    ACCOUNT_CHANGE = "account_change"
    PURCHASE = "purchase"


@dataclass(frozen=True)
class ScreenState:
    location: str
    indicators: frozenset[str] = frozenset()
    timers: dict[str, int] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass(frozen=True)
class Action:
    id: str
    target: str
    risk: Risk = Risk.NONE
    expected: str = ""


class DeviceAdapter(Protocol):
    def observe(self) -> ScreenState: ...
    def act(self, action: Action) -> None: ...


class UnsafeAction(RuntimeError):
    pass


class VerificationFailed(RuntimeError):
    pass


class VerifiedRuntime:
    """Executes one safe action and proves the resulting state changed."""

    def __init__(self, device: DeviceAdapter, allowed_risks: frozenset[Risk] = frozenset({Risk.NONE})):
        self.device = device
        self.allowed_risks = allowed_risks
        self.failures: dict[str, int] = {}

    def execute(self, action: Action, verifier: Callable[[ScreenState, ScreenState], bool]) -> ScreenState:
        before = self.device.observe()
        if before.confidence < 0.8:
            raise UnsafeAction("screen confidence is too low")
        if action.risk not in self.allowed_risks:
            raise UnsafeAction(f"blocked risk: {action.risk.value}")
        self.device.act(action)
        after = self.device.observe()
        if verifier(before, after):
            self.failures[action.id] = 0
            return after
        self.failures[action.id] = self.failures.get(action.id, 0) + 1
        raise VerificationFailed(f"{action.id} did not produce {action.expected or 'its expected state'}")


def indicator_removed(name: str) -> Callable[[ScreenState, ScreenState], bool]:
    return lambda before, after: name in before.indicators and name not in after.indicators
