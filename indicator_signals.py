# indicator_signals.py
"""Sinais de trading derivados apenas de indicadores e dados de cotação (sem LLM)."""
from __future__ import annotations

from typing import Any, Dict, Tuple


def signal_from_indicators(symbol_data: Dict[str, Any]) -> Tuple[float, str]:
    """
    Retorna (sentiment_score, recommendation) com score em [0, 1] e
    recommendation em {"BUY", "SELL", "HOLD"}.
    """
    rsi = float(symbol_data.get("rsi", 50.0))
    macd = str(symbol_data.get("macd_trend", "neutral")).lower()
    ema = str(symbol_data.get("ema_trend", "neutral")).lower()
    ratio = float(symbol_data.get("bid_ask_ratio", 1.0))

    score = 0.5

    if rsi < 30.0:
        score += 0.16
    elif rsi > 70.0:
        score -= 0.16
    elif rsi < 42.0:
        score += 0.06
    elif rsi > 58.0:
        score -= 0.06

    if macd == "bullish" and ema == "bullish":
        score += 0.14
    elif macd == "bearish" and ema == "bearish":
        score -= 0.14
    elif macd == "bullish" or ema == "bullish":
        score += 0.07
    elif macd == "bearish" or ema == "bearish":
        score -= 0.07

    if ratio > 1.08:
        score += 0.05
    elif ratio < 0.92:
        score -= 0.05

    score = max(0.0, min(1.0, score))

    if score >= 0.58:
        recommendation = "BUY"
    elif score <= 0.42:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return score, recommendation
