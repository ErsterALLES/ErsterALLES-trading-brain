import pytest

from trading_brain import RiskLimits, enforce_position_cap


def test_enforce_position_cap_allows_within_limits() -> None:
    limits = RiskLimits(max_notional_per_trade=100.0, max_open_notional=500.0)
    enforce_position_cap(proposed_notional=50.0, open_notional=400.0, limits=limits)


def test_enforce_position_cap_rejects_per_trade_breach() -> None:
    limits = RiskLimits(max_notional_per_trade=10.0, max_open_notional=500.0)
    with pytest.raises(ValueError, match="max_notional_per_trade"):
        enforce_position_cap(proposed_notional=20.0, open_notional=0.0, limits=limits)


def test_enforce_position_cap_rejects_portfolio_breach() -> None:
    limits = RiskLimits(max_notional_per_trade=100.0, max_open_notional=500.0)
    with pytest.raises(ValueError, match="max_open_notional"):
        enforce_position_cap(proposed_notional=80.0, open_notional=450.0, limits=limits)
