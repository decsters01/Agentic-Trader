# Plano de implementação: trading só com indicadores (zero LLM)

> **Para workers agenticos:** SUB-SKILL OBRIGATÓRIA: usar `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa a tarefa. Os passos usam checkbox (`- [ ]`) para acompanhamento.

**Objetivo:** Eliminar completamente chamadas a modelos de linguagem (OpenAI, Groq, Cerebras, LiteLLM, OpenAI Agents SDK) e fazer o ciclo de trading decidir apenas com dados numéricos e indicadores já calculados (RSI, MACD, EMA, bid/ask, volume, LTP).

**Arquitetura:** Um módulo puro `indicator_signals.py` calcula `(sentiment_score, recommendation)` a partir de um dicionário `symbol_data` idêntico ao que `market_data.py` já produz. A classe atual em `ai_agent.py` deixa de receber cliente LLM; `analyze_market_sentiment` passa a delegar ao módulo de sinais (ou é substituída por um método que aceita `dict`). `config.py` remove `setup_model` e constantes de provedor. `main.py` deixa de inicializar modelo. Dependências `openai` e `openai-agents` saem do `pyproject.toml`. Testes `pytest` cobrem a função de sinal com casos fixos.

**Stack:** Python 3.12+, OpenAlgo, APScheduler, TA-Lib (via `utils.calculate_technical_indicators`), pytest para verificação.

**Nota de contexto (brainstorming):** O ideal é trabalhar num worktree dedicado antes de implementar; se já estás na branch certa, ignora.

---

## Mapa de ficheiros

| Ficheiro | Responsabilidade |
|----------|-------------------|
| `indicator_signals.py` (novo) | Funções puras: mapear RSI/MACD/EMA/bid_ask → score 0..1 e recomendação BUY/SELL/HOLD. |
| `ai_agent.py` (alterar) | Remover imports/uso de API; `__init__` sem cliente; `analyze_market_sentiment` aceita `dict` ou novo nome `signal_from_market_data`. Manter `analyze_past_trades`, `decide_action`, `generate_learning_insights_static`. |
| `config.py` (alterar) | Apagar `setup_model`, `MODEL_PROVIDER`, nomes de modelo, `TEMPERATURE`. Manter limiares `SENTIMENT_THRESHOLD_*` usados por `decide_action`. |
| `main.py` (alterar) | Imports: remover `setup_model`, `MODEL_PROVIDER`; não guardar `trading_model`; `initialize_system` devolve tupla sem modelo; `run_trading_cycle` passa `symbol_data` ao agente em vez de string; assinaturas de `schedule_jobs` / `main_async` sem objeto de modelo. |
| `pyproject.toml` (alterar) | Remover `openai>=...` e `openai-agents[...]`. Acrescentar `[project.optional-dependencies] dev = ["pytest>=8.0.0"]`. Opcional: descrição do projeto sem “IA Autônoma” se quiseres alinhar marketing ao código. |
| `tests/test_indicator_signals.py` (novo) | Testes da função de sinal. |
| `uv.lock` | Regenerar com `uv lock` após alterar dependências. |

**Fora de âmbito deste plano (YAGNI):** treinar um modelo clássico/ML com dados do repositório; isso fica para um plano futuro se ainda precisares de predição não baseada em regras.

---

### Task 1: Função pura de sinal a partir de indicadores

**Ficheiros:**
- Criar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\indicator_signals.py`
- Teste: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\tests\test_indicator_signals.py`

- [ ] **Passo 1: Escrever o teste que falha**

Criar pasta `tests` e ficheiro com:

```python
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
```

- [ ] **Passo 2: Correr o teste e confirmar que falha**

Executar:

```powershell
Set-Location "c:\Users\gabde\Downloads\superbot\Agentic-Trader"
python -m pytest tests\test_indicator_signals.py -v
```

Esperado: `ModuleNotFoundError: No module named 'indicator_signals'` ou `ImportError`.

- [ ] **Passo 3: Implementação mínima**

Criar `indicator_signals.py`:

```python
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
```

- [ ] **Passo 4: Correr os testes até passarem**

```powershell
python -m pytest tests\test_indicator_signals.py -v
```

Esperado: quatro testes `PASSED`.

- [ ] **Passo 5: Commit**

```bash
git add indicator_signals.py tests/test_indicator_signals.py
git commit -m "feat: sinais de trading só com indicadores (sem LLM)"
```

---

### Task 2: Agente sem cliente LLM

**Ficheiros:**
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\ai_agent.py`

- [ ] **Passo 1: Escrever teste de integração leve do agente**

Criar `tests/test_ai_agent_rules.py`:

```python
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
```

- [ ] **Passo 2: Correr e ver falha**

```powershell
python -m pytest tests\test_ai_agent_rules.py -v
```

Esperado: falha por `AIAgent()` exigir argumento ou método antigo com string/LLM.

- [ ] **Passo 3: Refatorar `ai_agent.py`**

Substituir o conteúdo relevante por:

1. Remover `import json` se já não for usado neste módulo (mantém se ainda usado em outro método do mesmo ficheiro — hoje não há outro uso que não seja LLM; remover `json`).
2. Remover referências a `MODEL_PROVIDER` no método de análise.
3. `__init__(self)` sem parâmetros.
4. Novo contrato para análise (escolhe um dos dois e usa em todo o código no Task 3 de forma consistente):

**Opção A (recomendada):** renomear para clareza mantendo compatibilidade:

```python
def analyze_market_sentiment(self, symbol_data: dict) -> tuple:
    from indicator_signals import signal_from_indicators
    score, recommendation = signal_from_indicators(symbol_data)
    print(f"{Fore.CYAN}[SINAL] score={score:.2f}, recomendação={recommendation}{Style.RESET_ALL}", flush=True)
    return score, recommendation
```

Apagar completamente o bloco `try/except` com `self.client.chat.completions.create`, o `prompt` e o `model_map` (e qualquer `os.getenv` de modelo — o ficheiro atual nem importa `os`; esse bloco está quebrado em runtime para providers não-openai).

Manter inalterados os métodos: `analyze_past_trades`, `generate_learning_insights_static`, `generate_learning_insights`, `decide_action`.

Atualizar docstring da classe para: decisão assistida por regras e histórico, sem modelo de linguagem.

- [ ] **Passo 4: Correr testes**

```powershell
python -m pytest tests\test_ai_agent_rules.py tests\test_indicator_signals.py -v
```

Esperado: todos `PASSED`.

- [ ] **Passo 5: Commit**

```bash
git add ai_agent.py tests/test_ai_agent_rules.py
git commit -m "refactor: AIAgent sem cliente LLM; sinais só por indicadores"
```

---

### Task 3: Config e entrada principal sem modelo

**Ficheiros:**
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\config.py` (remover linhas 12–83 aprox.: bloco de modelo e função `setup_model`; remover `TEMPERATURE` e uso de `MODEL_TEMPERATURE`; remover constantes `DEFAULT_*MODEL*` e `MODEL_PROVIDER` se não forem mais referenciadas)
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\main.py`

- [ ] **Passo 1: Teste de fumo de importação**

Criar `tests/test_main_imports.py`:

```python
# tests/test_main_imports.py
def test_main_module_imports_without_litellm():
    import importlib
    m = importlib.import_module("main")
    assert hasattr(m, "initialize_system")
    assert hasattr(m, "run_trading_cycle")
```

- [ ] **Passo 2: Correr teste (deve falhar até remover setup_model)**

```powershell
python -m pytest tests\test_main_imports.py -v
```

Esperado: `ModuleNotFoundError: agents...` ou erro de import enquanto `config.setup_model` existir.

- [ ] **Passo 3: Editar `config.py`**

- Apagar por completo a função `setup_model` e todos os imports condicionais a `LitellmModel`.
- Apagar variáveis: `DEFAULT_MODEL_PROVIDER`, `DEFAULT_CEREBRAS_MODEL`, `DEFAULT_GROQ_MODEL`, `DEFAULT_CUSTOM_MODEL`, `DEFAULT_OPENAI_MODEL`, `MODEL_PROVIDER`, `TEMPERATURE`, `DEFAULT_TEMPERATURE` (e a linha que lê `MODEL_TEMPERATURE`).
- Manter: `SENTIMENT_THRESHOLD_BUY`, `SENTIMENT_THRESHOLD_SELL`, `VOLATILITY_THRESHOLD` (se usado em `trading_engine` ou outro sítio — verificar com grep antes de apagar).

- [ ] **Passo 4: Editar `main.py`**

Alterações concretas:

1. No import de `config`, remover `setup_model` e `MODEL_PROVIDER`.
2. Em `initialize_system()`:
   - Remover linhas `trading_model, model_name = setup_model()` e qualquer print associado.
   - Trocar `ai_agent = AIAgent(trading_model)` por `ai_agent = AIAgent()`.
   - Alterar `return` para: `return client, market_client, trading_engine, ai_agent, trade_state` (cinco valores).
3. Em `main_async()`:
   - Desempacotar: `client, market_client, trading_engine, ai_agent, trade_state = initialize_system()`.
4. Em `run_trading_cycle`, remover a construção da string longa `market_summary` e chamar:

```python
sentiment_score, recommendation = ai_agent.analyze_market_sentiment(symbol_data)
```

5. Em `reset_daily_state`, manter `AIAgent.generate_learning_insights_static(trade_state)` (continua válido).

6. Atualizar docstrings que mencionam “modelo de IA”.

- [ ] **Passo 5: Correr pytest na pasta tests**

```powershell
python -m pytest tests\ -v
```

Esperado: todos os testes `PASSED`.

- [ ] **Passo 6: Commit**

```bash
git add config.py main.py tests/test_main_imports.py
git commit -m "chore: remover setup_model e fluxo LLM da entrada principal"
```

---

### Task 4: Dependências e lockfile

**Ficheiros:**
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\pyproject.toml`
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\uv.lock` (regenerado)

- [ ] **Passo 1: Editar `pyproject.toml`**

Remover estas linhas da lista `dependencies`:

```toml
    "openai>=1.0.0",
    "openai-agents[litellm,sqlalchemy]>=0.1.0",
```

Acrescentar ao final do ficheiro (se ainda não existir grupo dev):

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0.0"]
```

- [ ] **Passo 2: Regenerar lock e instalar ambiente de dev**

```powershell
Set-Location "c:\Users\gabde\Downloads\superbot\Agentic-Trader"
uv lock
uv sync --extra dev
```

Esperado: `uv lock` completa sem erro; `uv sync` instala pytest.

- [ ] **Passo 3: Confirmar que não há import `agents` ou `openai` no código da app**

```powershell
Get-ChildItem -Recurse -Filter *.py | Select-String -Pattern "litellm|LitellmModel|openai\.|from agents|import agents" -Path . -Exclude @("*\tests\*")
```

Ou com ripgrep:

```powershell
rg "litellm|LitellmModel|from agents|openai_agents" --glob "*.py" --glob "!tests/"
```

Esperado: nenhuma correspondência nos módulos de aplicação (apenas eventualmente em documentação — ignorar ou limpar na Task 5).

- [ ] **Passo 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: remover openai e openai-agents; adicionar extra dev com pytest"
```

---

### Task 5: Alinhamento de documentação e exemplos de env (opcional mas recomendado)

**Ficheiros:**
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\.env.example` — remover ou comentar blocos `OPENAI_API_KEY`, `GROQ_API_KEY`, `CEREBRAS_API_KEY`, `MODEL_PROVIDER`, `OPENAI_MODEL`, etc., e acrescentar uma linha: `# Decisões: apenas indicadores (ver indicator_signals.py). Sem LLM.`
- Modificar: `c:\Users\gabde\Downloads\superbot\Agentic-Trader\README.md` e `MODEL_CONFIG.md` — apagar secções que instruem configuração de LLM e substituir por duas frases: decisão por regras em `indicator_signals.py`; para alterar comportamento, ajustar limiares em `config.py` (`SENTIMENT_THRESHOLD_*`) e a função de sinal.

- [ ] **Passo 1:** Aplicar edições literais acima nos três ficheiros.
- [ ] **Passo 2:** Commit: `docs: remover instruções de LLM; documentar modo só indicadores`

---

## Revisão (self-review)

**1. Cobertura do pedido:**  
- Sem LLM no runtime: Tasks 1–4.  
- “Treinar um modelo básico depois”: explicitamente **não** coberto (plano futuro).  
- Remoção de dependências LLM: Task 4.  
- Documentação: Task 5.

**2. Scan de placeholders:** Nenhum `TBD` / `implement later`.

**3. Consistência de tipos:** `analyze_market_sentiment(self, symbol_data: dict) -> tuple` alinhado com `main.py` que passa `symbol_data` dict; `decide_action` mantém a mesma assinatura.

---

## Handoff de execução

**Plano completo e guardado em** `docs/superpowers/plans/2026-04-23-trading-sem-llm-indicadores.md`.

**Duas opções de execução:**

1. **Subagent-Driven (recomendado)** — um subagente por tarefa, revisão entre tarefas, iteração rápida.  
2. **Inline Execution** — executar as tarefas nesta sessão com checkpoints para revisão (`executing-plans`).

**Qual preferes?**

Se escolheres **Subagent-Driven**, a SUB-SKILL obrigatória é `superpowers:subagent-driven-development`.  
Se escolheres **Inline Execution**, usa `superpowers:executing-plans`.
