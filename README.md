# Agente Autônomo de Trading

> **Editado, Melhorado e Adaptado por Gabriel Decsters**

> Sistema de trading algorítmico com decisão por **indicadores e regras** (sem LLM).

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um agente de trading que analisa indicadores técnicos em tempo real, gera sinais COMPRA/VENDA/MANTER em `indicator_signals.py` e executa ordens via OpenAlgo na NSE (Bolsa Nacional da Índia).

---

## Destaques

- 70% mais velocidade de execução (3-6s vs 12-20s por ciclo)
- Sem custos nem latência de API de modelo de linguagem
- 7 indicadores técnicos (RSI, MACD, Bandas de Bollinger, EMA, Estocástico, ADX, ATR)
- Busca de dados em paralelo (todas as 5 ações simultaneamente)
- Ordens de mercado instantâneas (sem espera para preenchimento de ordens limitadas)
- Gerenciamento rigoroso de riscos (stop-loss, limites de posição, sem pirâmide)
- Decisão por regras e indicadores (`indicator_signals.py`), sem LLM
- Shorting habilitado (pode assumir posições longas ou short)

---

## Índice

- [Início Rápido](#início-rápido)
- [Funcionalidades](#funcionalidades)
- [Desempenho](#desempenho)
- [Como Funciona](#como-funciona)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Gerenciamento de Riscos](#gerenciamento-de-riscos)
- [Documentação](#documentação)
- [Solução de Problemas](#solução-de-problemas)
- [Aviso Legal](#aviso-legal)

---

## Início Rápido

```bash
# 1. Clonar o repositório
git clone https://github.com/marketcalls/Agentic-Trader.git
cd Agentic-Trader

# 2. Instalar o gerenciador de pacotes uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Instalar dependências (inclui pytest com --extra dev)
uv sync --extra dev

# 4. Configurar ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# 5. Executar o agente
uv run python main.py
```

É isso! O agente começará a operar automaticamente a cada 5 minutos durante o horário de funcionamento do mercado (9:15 AM - 3:30 PM IST).

---

## Funcionalidades

### Capacidades Principais

| Funcionalidade | Descrição |
|---------|-------------|
| **5 Ações** | ICICIBANK, RELIANCE, SBIN, WIPRO, ITC |
| **7 Indicadores de AT** | RSI, MACD, Bandas de Bollinger, EMA, Estocástico, ADX, ATR |
| **Processamento Paralelo** | Busca todos os dados simultaneamente em 2-3 segundos |
| **Ordens de Mercado** | Execução instantânea (sem espera para preenchimento) |
| **Operações em Lote** | Realiza múltiplas ordens de uma vez |
| **Shorting** | Pode vender sem possuir (cria posição short) |
| **Controles de Risco** | Stop-loss, limites de trades, restrições de posição |
| **Sem LLM** | Sinais em `indicator_signals.py`; limiares em `config.py` |
| **Auto-Agendamento** | Executa a cada 5 minutos durante horário de mercado |
| **Risco** | Limites diários e por símbolo no motor de trading |

### Análise Técnica

O agente usa **7 indicadores profissionais TA-Lib**:

1. **RSI** - Identifica condições de sobrecompra/sobrevenda
2. **MACD** - Detecta momentum e direção da tendência
3. **Bandas de Bollinger** - Mede volatilidade e extremos de preço
4. **EMA** - Acompanha a direção da tendência (20 e 50 períodos)
5. **Estocástico** - Indicador de momentum para reversões
6. **ADX** - Mede força da tendência (não direção)
7. **ATR** - Medida de volatilidade para stop-loss

**Lógica de Trading**: Requer 3+ indicadores alinhados para acionar COMPRA/VENDA. Sinais fracos = MANTER.

---

## Desempenho

### Antes vs Depois da Otimização

| Métrica | Antes | Depois | Melhoria |
|--------|--------|-------|-------------|
| **Tempo de Ciclo** | 12-20s | 3-6s | 70% mais rápido |
| **Busca de Dados** | 8-12s | 2-3s | 75% mais rápido |
| **Uso de Tokens** | 144K | 30K | 79% redução |
| **Custo por Ciclo** | $0.023-0.031 | $0.008-0.012 | 65% mais barato |
| **Execução de Ordens** | 15-45s | Instantâneo | 100% mais rápido |
| **Custo Mensal** | $74 | $26 | Economia de $48/mês |

*Custos calculados usando o modelo Cerebras llama3.1-8b*

### Desempenho no Mundo Real

- **Busca de dados**: 2-3 segundos para todas as 5 ações (paralelo)
- **Tomada de decisão**: 1-2 segundos (7 indicadores analisados)
- **Execução de ordens**: < 1 segundo (ordens de mercado)
- **Ciclo total**: 3-6 segundos end-to-end
- **Ciclos por dia**: ~75 (a cada 5 minutos, 9:15 AM - 3:30 PM)

---

## Como Funciona

### Ciclo de Trading (A Cada 5 Minutos)

```
1. BUSCAR DADOS (Paralelo - 2-3s)
   ↓
   Busca cotações, profundidade e 7 indicadores de AT para todas as 5 ações simultaneamente

2. ANALISAR (Por Ação)
   ↓
   • Examina RSI, MACD, Bandas de Bollinger, EMA, Estocástico, ADX, ATR
   • Verifica por 3+ sinais alinhados
   • Toma decisão de COMPRA/VENDA/MANTER

3. VALIDAR (Verificação de Risco)
   ↓
   • Verifica stop-loss diário (-Rs.10.000)
   • Verifica limites de trades (5 por ação)
   • Garante sem pirâmide de posições

4. CALCULAR (Tamanho da Posição)
   ↓
   • Investimento fixo de Rs.10.000 por trade
   • Quantidade = int(10000 / LTP)

5. EXECUTAR (Ordens em Lote - Paralelo)
   ↓
   • Realiza todas as ordens simultaneamente
   • Ordens de mercado (execução instantânea)
   • Rate limiting (0.5s a cada 2 ordens)
```

### Exemplo de Saída

```
================================================================================
Ciclo de Trading: 2025-01-15 10:30:00 IST
================================================================================

[DADOS EM LOTE] Buscando dados para 5 símbolos em paralelo...
[DADOS EM LOTE] Completado em 2.3 segundos

ICICIBANK: COMPRAR Ordem#123 (MACD bullish)
RELIANCE: MANTER (sinais fracos)
SBIN: MANTER (posição existente)
WIPRO: VENDER Ordem#124 (take profit)
ITC: MANTER (sinais mistos)

================================================================================
[USO DE TOKENS] Estatísticas de Chamadas API:
  Requisições:      3
  Tokens de Entrada:  28.234
  Tokens de Saída: 2.851
  Total de Tokens:  31.085
  Custo Est.:     $0.008
================================================================================
```

---

## Instalação

### Pré-requisitos

1. **Python 3.12+** - [Baixar Python](https://www.python.org/downloads/)
2. **Gerenciador de pacotes uv** - [Instalar uv](https://github.com/astral-sh/uv)
3. **Biblioteca TA-Lib** - [Instalar TA-Lib](https://ta-lib.org/)
4. **Chaves de API**:
   - Conta e API **OpenAlgo** (único serviço externo obrigatório para ordens e dados)

### Instalação Passo a Passo

#### 1. Instalar Python 3.12+

```bash
# Verificar versão do Python
python --version  # Deve ser 3.12 ou superior
```

#### 2. Instalar gerenciador de pacotes uv

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. Instalar TA-Lib (Específico por Plataforma)

**Windows:**
```bash
# Baixar de: https://ta-lib.org/
# Instalar o instalador .exe
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ta-lib
```

**Mac:**
```bash
brew install ta-lib
```

#### 4. Clonar e Instalar Projeto

```bash
# Clonar repositório
git clone <repo-url>
cd autonomous-agents

# Instalar dependências
uv sync

# Instalar wrapper Python do TA-Lib
uv pip install TA-Lib
```

---

## Configuração

### 1. Criar Arquivo de Ambiente

```bash
cp .env.example .env
```

### 2. Editar `.env`

Define apenas as variáveis **OpenAlgo** (e opcionalmente limiares de decisão). Não são necessárias chaves de LLM.

```bash
OPENALGO_API_KEY=your-openalgo-api-key
OPENALGO_HOST=http://127.0.0.1:5000
# Opcional: SENTIMENT_THRESHOLD_BUY, SENTIMENT_THRESHOLD_SELL
```

Detalhes em [MODEL_CONFIG.md](./MODEL_CONFIG.md).

---

## Uso

### Executando o Agente

#### Modo Desenvolvimento (com Ciclo de Teste)

```bash
uv run python main.py
```

Isso irá:
- Executar um ciclo de teste imediato
- Depois agendar ciclos a cada 5 minutos durante o horário de mercado

#### Modo Produção (Apenas Agendado)

1. Edite `main.py` e comente a linha do ciclo de teste:
   ```python
   # await run_trading_cycle()  # Comente esta linha
   ```

2. Execute o agente:
   ```bash
   uv run python main.py
   ```

O agente será executado apenas durante o horário agendado de mercado (9:15 AM - 3:30 PM IST, Segunda-Sexta).

### Agenda de Trading

| Evento | Horário | Descrição |
|-------|------|-------------|
| **Ciclos de Trading** | 9:15 AM - 3:30 PM | A cada 5 minutos |
| **Square-Off** | 3:15 PM | Fechar todas as posições |
| **Reset Diário** | 3:45 PM | Resetar contagem de trades e P&L |

### Monitoramento

O agente fornece saída em tempo real:

- 🔵 **Azul** - Dados de mercado buscados
- 🟢 **Verde** - Informações da conta
- 🟡 **Amarelo** - Avisos de risco
- 🔴 **Vermelho** - Erros ou trades bloqueados
- ⚪ **Branco** - Decisões de trading
- 🟣 **Magenta** - Execução de ordens
- 🔷 **Ciano** - Informações do sistema

---

## Gerenciamento de Riscos

### Recursos de Segurança Integrados

#### 1. Stop-Loss Diário
- **Limite**: -Rs.10.000 de perda diária
- **Ação**: Interrompe todo trading quando atingido

#### 2. Limites de Contagem de Trades
- **Limite**: 5 trades por ação por dia
- **Previne**: Over-trading (excesso de operações)

#### 3. Controle de Posição
- **Sem Pirâmide**: Não pode adicionar a posições long/short existentes
- **COMPRAR** apenas se não houver posição long
- **VENDER** apenas se não houver posição short

#### 4. Regras de Shorting
✅ **Permitido:**
- VENDER sem posição (cria short)
- COMPRAR para fechar posição short

❌ **Bloqueado:**
- Adicionar a posição long existente
- Adicionar a posição short existente

#### 5. Tamanho Fixo de Posição
- **Investimento**: Rs.10.000 por trade
- **Previne**: Over-leverage (alavancagem excessiva)

### Parâmetros de Trading

```python
SYMBOLS = ["ICICIBANK", "RELIANCE", "SBIN", "WIPRO", "ITC"]
MAX_INVESTMENT_PER_TRADE = 10000  # Rs.10.000 por trade
DAILY_STOP_LOSS = -10000          # Máx -Rs.10.000 perda/dia
MAX_TRADES_PER_SYMBOL = 5         # Máx 5 trades por ação/dia
EXCHANGE = "NSE"
PRODUCT = "MIS"                   # Trading intradiário
```

---

## Documentação

### Documentos Principais

- **[README.md](./README.md)** - Este arquivo (Guia de início rápido)
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitetura detalhada do sistema
- **[MODEL_CONFIG.md](./MODEL_CONFIG.md)** - Configuração do provedor de modelo
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Problemas comuns e soluções

### Links Rápidos

| Tópico | Link |
|-------|------|
| Visão Geral da Arquitetura | [ARCHITECTURE.md](./ARCHITECTURE.md#architecture-design) |
| Ferramentas de Trading | [ARCHITECTURE.md](./ARCHITECTURE.md#trading-tools) |
| Gerenciamento de Riscos | [ARCHITECTURE.md](./ARCHITECTURE.md#risk-management) |
| Métricas de Desempenho | [ARCHITECTURE.md](./ARCHITECTURE.md#performance-optimization) |
| Decisão por indicadores | [MODEL_CONFIG.md](./MODEL_CONFIG.md) |
| Problemas Comuns | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) |

---

## Solução de Problemas

### Problemas Comuns

#### 1. Erro de Importação: Módulo não encontrado

```bash
uv sync --extra dev
```

#### 2. Erro de Importação do TA-Lib

```bash
# Instale o binário do TA-Lib primeiro (veja a seção Instalação)
# Depois instale o wrapper Python:
uv pip install TA-Lib
```

#### 3. Limite de Taxa Excedido

Edite `main.py` e aumente os delays:
```python
# Na função get_all_market_data():
time.sleep(0.2)  # Aumentar de 0.15
```

#### 4. Erro de Autenticação OpenAlgo

Verifique o `.env`:
- `OPENALGO_API_KEY` e `OPENALGO_HOST` corretos
- Serviço OpenAlgo acessível no host configurado

Para mais ajuda com solução de problemas, veja [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

---

## Estrutura do Projeto

```
autonomous-agents/
├── main.py                  # Agente de trading principal (execute este)
├── indicator_signals.py     # Score e BUY/SELL/HOLD a partir de indicadores
├── .env                     # Suas chaves de API (gitignored)
├── .env.example            # Modelo de configuração de exemplo
├── pyproject.toml          # Dependências Python
├── uv.lock                 # Arquivo lock de dependências
├── .gitignore              # Regras de ignore do Git
├── README.md               # Este arquivo
├── ARCHITECTURE.md         # Documentação detalhada da arquitetura
├── MODEL_CONFIG.md         # Sinais por indicadores (sem LLM)
├── TROUBLESHOOTING.md      # Problemas comuns e correções
└── trading_memory.db       # Banco de dados do histórico de trades (gitignored)
```

---

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para enviar um Pull Request.

### Configuração de Desenvolvimento

```bash
# Clonar para desenvolvimento
git clone <repo-url>
cd autonomous-agents

# Criar ambiente virtual
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
uv sync

# Rodar testes (se disponível)
uv run pytest
```

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

---

## Aviso Legal

**IMPORTANTE: DIVULGAÇÃO DE RISCOS DE TRADING**

Este é um **sistema autônomo de trading com IA** que toma decisões reais de trading sem intervenção humana.

**Riscos Incluídos:**
- Perda financeira substancial
- Volatilidade do mercado
- Falhas técnicas
- Erros de decisão da IA
- Problemas no broker/API

**Antes de Usar:**
1. ✅ Teste em **modo paper trading** primeiro
2. ✅ Entenda todos os parâmetros de risco
3. ✅ Comece com capital pequeno
4. ✅ Monitore frequentemente
5. ✅ Tenha stop-loss configurado

**Aviso Legal:**
- Use por sua conta e risco
- Sem garantias de lucro
- Desempenho passado ≠ resultados futuros
- Não é aconselhamento financeiro
- Você é responsável por todos os trades

**Os autores e contribuidores não são responsáveis por quaisquer perdas financeiras incorridas.**

---

## Recursos

### Documentação Oficial

- **TA-Lib**: https://ta-lib.org/
- **OpenAlgo**: https://openalgo.in/

### Suporte

- **GitHub Issues**: [Reportar bugs ou solicitar funcionalidades]
- **Documentação**: Veja a pasta `docs/`
- **Email**: [Seu email de suporte]

---

## Roadmap de Funcionalidades

**Melhorias Planejadas:**

- [ ] Dashboard web para monitoramento
- [ ] Engine de backtesting
- [ ] Modo paper trading
- [ ] Suporte a múltiplas estratégias
- [ ] Gerenciamento de portfólio
- [ ] Alertas por email/SMS
- [ ] Análise de desempenho
- [ ] Suporte a múltiplas exchanges
- [ ] Trading de opções
- [ ] Análise de sentimento de notícias

---

## Estatísticas

- **Linhas de Código**: ~1.000
- **Dependências**: ver `pyproject.toml` / `uv.lock`
- **Ações Suportadas**: 5 (expansível)
- **Indicadores Técnicos**: 7
- **Sessões de Trading por Dia**: ~75 ciclos
- **Tempo Médio de Ciclo**: 3-6 segundos
---

**Versão**: modo só indicadores (sem LLM)
**Status**: em desenvolvimento; testar em paper antes de capital real

---

## Comandos Rápidos

```bash
# Instalar e executar
uv sync && uv run python main.py

# Verificar logs
tail -f trading_agent.log

# Ver trades recentes
sqlite3 trading_memory.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10"
```

---

**Bom Trading!**
