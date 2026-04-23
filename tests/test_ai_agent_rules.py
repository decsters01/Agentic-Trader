# tests/test_ai_agent_rules.py
from config import SENTIMENT_THRESHOLD_BUY, SENTIMENT_THRESHOLD_SELL
from ai_agent import AIAgent


def test_analyze_market_data_dict_returns_tuple():
    agent = AIAgent()
    data = {
        "rsi": 28.0,
        "macd_trend": "bullish",
        "ema_trend": "bullish",
        "bid_ask_ratio": 1.1,
        "ltp": 10.0,
        "volume": 1000,
    }
    score, rec = agent.analyze_market_sentiment(data)
    assert isinstance(score, float)
    assert rec in ("BUY", "SELL", "HOLD")


def test_decide_action_blocks_when_risk_disallows():
    agent = AIAgent()
    past = {"confidence": "high", "symbol": "X", "win_rate": 0.7}
    risk = {"allowed": False, "reason": "test"}
    assert agent.decide_action(0.9, "BUY", risk, past) == "HOLD"


def test_decide_action_buy_confirmed_with_score_and_confidence():
    agent = AIAgent()
    risk = {"allowed": True, "reason": "ok"}
    past = {"confidence": "high", "symbol": "X", "win_rate": 0.7}
    score = max(SENTIMENT_THRESHOLD_BUY, 0.65)
    assert agent.decide_action(score, "BUY", risk, past) == "BUY"


def test_decide_action_buy_hold_when_confidence_low():
    agent = AIAgent()
    risk = {"allowed": True, "reason": "ok"}
    past = {"confidence": "low", "symbol": "X", "win_rate": 0.2}
    score = max(SENTIMENT_THRESHOLD_BUY, 0.65)
    assert agent.decide_action(score, "BUY", risk, past) == "HOLD"


def test_decide_action_sell_confirmed_with_score_and_confidence():
    agent = AIAgent()
    risk = {"allowed": True, "reason": "ok"}
    past = {"confidence": "medium", "symbol": "X", "win_rate": 0.5}
    score = min(SENTIMENT_THRESHOLD_SELL, 0.25)
    assert agent.decide_action(score, "SELL", risk, past) == "SELL"


def test_decide_action_sell_hold_when_confidence_low():
    agent = AIAgent()
    risk = {"allowed": True, "reason": "ok"}
    past = {"confidence": "low", "symbol": "X", "win_rate": 0.2}
    score = min(SENTIMENT_THRESHOLD_SELL, 0.25)
    assert agent.decide_action(score, "SELL", risk, past) == "HOLD"
