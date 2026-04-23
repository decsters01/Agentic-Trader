# Decisão por indicadores (sem LLM)

O motor de decisão **não** chama APIs de modelos de linguagem. O fluxo é:

1. **`market_data.py`** obtém LTP, volume, book e histórico; calcula RSI, tendência MACD e tendência EMA (entre outros via `utils`).
2. **`indicator_signals.py`** combina esses campos num **score 0..1** e numa recomendação **BUY / SELL / HOLD**.
3. **`ai_agent.py`** aplica histórico de trades (`analyze_past_trades`) e **`decide_action`** cruza o score com `SENTIMENT_THRESHOLD_BUY` e `SENTIMENT_THRESHOLD_SELL` em `config.py`, mais a análise de risco do `TradingEngine`.

## O que ajustar

- **Sensibilidade dos sinais:** edita os limiares e pesos em `indicator_signals.py`.
- **Gates de compra/venda após o sinal:** variáveis de ambiente `SENTIMENT_THRESHOLD_BUY` e `SENTIMENT_THRESHOLD_SELL` (ver `config.py`).

## Execução

```bash
uv sync --extra dev
cp .env.example .env
# Preencher OPENALGO_* no .env
uv run python main.py
```

## Testes

```bash
uv run pytest tests/ -v
```
