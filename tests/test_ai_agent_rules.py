# tests/test_ai_agent_rules.py
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
