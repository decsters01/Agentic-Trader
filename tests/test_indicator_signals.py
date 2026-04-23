# tests/test_indicator_signals.py
import pytest

from indicator_signals import signal_from_indicators


def test_oversold_bullish_bias_buy_or_high_score():
    data = {
        "ltp": 100.0,
        "volume": 1_000_000,
        "bid_ask_ratio": 1.2,
        "rsi": 25.0,
        "macd_trend": "bullish",
        "ema_trend": "bullish",
    }
    score, rec = signal_from_indicators(data)
    assert score >= 0.55
    assert rec == "BUY"


def test_overbought_bearish_bias_sell():
    data = {
        "ltp": 100.0,
        "volume": 500_000,
        "bid_ask_ratio": 0.85,
        "rsi": 78.0,
        "macd_trend": "bearish",
        "ema_trend": "bearish",
    }
    score, rec = signal_from_indicators(data)
    assert score <= 0.48
    assert rec == "SELL"


def test_neutral_cluster_hold():
    data = {
        "ltp": 50.0,
        "volume": 100_000,
        "bid_ask_ratio": 1.0,
        "rsi": 50.0,
        "macd_trend": "neutral",
        "ema_trend": "neutral",
    }
    score, rec = signal_from_indicators(data)
    assert 0.45 <= score <= 0.55
    assert rec == "HOLD"


def test_score_clamped_zero_one():
    data = {
        "rsi": 0.0,
        "macd_trend": "bearish",
        "ema_trend": "bearish",
        "bid_ask_ratio": 0.5,
    }
    score, _ = signal_from_indicators(data)
    assert 0.0 <= score <= 1.0
