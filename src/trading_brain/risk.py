from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RiskLimits:
    """Hard caps used before sending orders to a broker or simulator."""

    max_notional_per_trade: float
    max_open_notional: float


def enforce_position_cap(
    *,
    proposed_notional: float,
    open_notional: float,
    limits: RiskLimits,
) -> None:
    """Raise if a proposed trade would breach configured notional limits.

    Values are expressed in the same currency as the strategy's accounting basis.
    """

    if proposed_notional <= 0:
        msg = "proposed_notional must be positive"
        raise ValueError(msg)
    if open_notional < 0:
        msg = "open_notional cannot be negative"
        raise ValueError(msg)
    if proposed_notional > limits.max_notional_per_trade:
        msg = "proposed_notional exceeds max_notional_per_trade"
        raise ValueError(msg)
    if open_notional + proposed_notional > limits.max_open_notional:
        msg = "open_notional + proposed_notional exceeds max_open_notional"
        raise ValueError(msg)
