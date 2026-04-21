# Guia de Configuração de Modelos

O agente de trading autônomo é **agnóstico em relação ao modelo** e suporta modelos da OpenAI, Groq e Cerebras via LiteLLM.

## Modelos Suportados

### Cerebras (RECOMENDADO PARA TRADING - Ultra-Rápido)
- **Modelo**: `gpt-oss-120b` (modelo de 120 bilhões de parâmetros)
- **Velocidade**: ⚡ **ULTRA-RÁPIDO** - 1800+ tokens/segundo
- **Prós**: Inferência extremamente rápida (10x mais rápido que OpenAI), excelente para trading em tempo real, 120B parâmetros para raciocínio robusto
- **Contras**: Provedor mais novo, histórico limitado
- **Ideal para**: Trading em tempo real onde velocidade é crítica
- **API**: https://api.cerebras.ai/v1

### Groq (Rápido e Custo-Benefício)
- **Modelo**: `qwen/qwen3-32b` (Qwen 3, 32 bilhões de parâmetros)
- **Velocidade**: ⚡ Rápido - 200-500 tokens/segundo
- **Prós**: Inferência muito rápida, custo-benefício, forte suporte multilíngue
- **Contras**: Tamanho do modelo menor comparado aos outros
- **Ideal para**: Desenvolvimento, testes, decisões de alta frequência

### OpenAI (Padrão - Alta Qualidade)
- **Modelo**: `gpt-5-mini`
- **Velocidade**: 🐌 Mais lento - 50-100 tokens/segundo
- **Prós**: Alta qualidade, confiável, melhor raciocínio
- **Contras**: Mais lento, custo maior por token
- **Ideal para**: Trading em produção com tomada de decisão precisa onde velocidade é menos crítica

## Configuração

### Configurações do Arquivo .env

Adicione estas variáveis ao seu arquivo `.env`:

```bash
# Provedor do Modelo: "cerebras" (recomendado), "groq" ou "openai" (padrão)
MODEL_PROVIDER=cerebras

# Chave de API da Cerebras (necessária se usar Cerebras)
CEREBRAS_API_KEY=csk-sua-chave-api-cerebras-aqui

# Chave de API da Groq (necessária se usar Groq)
GROQ_API_KEY=gsk-sua-chave-api-groq-aqui

# Chave de API da OpenAI (necessária se usar OpenAI)
OPENAI_API_KEY=sk-sua-chave-api-openai-aqui

# Configurações do OpenAlgo (sempre necessárias)
OPENALGO_API_KEY=sua-chave-openalgo
OPENALGO_HOST=http://127.0.0.1:5000
```

## Alternando Modelos

### Usar Cerebras (Recomendado para Velocidade)
1. Defina `MODEL_PROVIDER=cerebras` no `.env`
2. Certifique-se de que `CEREBRAS_API_KEY` está configurada
3. Execute o agente:
   ```bash
   uv run python agent.py
   ```
4. Você verá: `[MODELO] Usando Cerebras (cerebras/gpt-oss-120b) - ULTRA-RÁPIDO`

### Usar Groq
1. Defina `MODEL_PROVIDER=groq` no `.env`
2. Certifique-se de que `GROQ_API_KEY` está configurada
3. Execute o agente:
   ```bash
   uv run python agent.py
   ```
4. Você verá: `[MODELO] Usando Groq (groq/qwen/qwen3-32b)`

### Usar OpenAI (Padrão)
1. Defina `MODEL_PROVIDER=openai` no `.env` (ou deixe não definido)
2. Certifique-se de que `OPENAI_API_KEY` está configurada
3. Execute o agente:
   ```bash
   uv run python agent.py
   ```
4. Você verá: `[MODELO] Usando OpenAI (openai/gpt-5-mini)`

## Avançado: Seleção Personalizada de Modelo

Você pode substituir o modelo padrão para cada provedor:

```bash
# Usar um modelo diferente da Cerebras
MODEL_PROVIDER=cerebras
CEREBRAS_MODEL=cerebras/gpt-oss-120b  # Padrão, ou tente cerebras/llama3.1-70b
CEREBRAS_API_KEY=csk-...

# Usar um modelo diferente da Groq
MODEL_PROVIDER=groq
GROQ_MODEL=groq/qwen/qwen3-32b  # Padrão, ou tente groq/llama-3.3-70b-versatile
GROQ_API_KEY=gsk-...

# Usar um modelo diferente da OpenAI
MODEL_PROVIDER=openai
OPENAI_MODEL=openai/gpt-4o
OPENAI_API_KEY=sk-...

# Usar qualquer modelo compatível com LiteLLM personalizado
MODEL_PROVIDER=custom
CUSTOM_MODEL=anthropic/claude-3-5-sonnet-20241022
CUSTOM_API_KEY=sk-ant-...
CUSTOM_API_BASE=https://api.anthropic.com/v1  # Opcional
```

## Lógica de Seleção do Modelo

O agente seleciona automaticamente o modelo com base em `MODEL_PROVIDER`:

```python
# De agent.py:36-56
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()

if MODEL_PROVIDER == "groq":
    trading_model = LitellmModel(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
else:
    trading_model = LitellmModel(
        model="openai/gpt-5-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
```

## Adicionando Modelos Personalizados

Para adicionar suporte a outros modelos compatíveis com LiteLLM:

1. Edite `agent.py` linhas 36-56
2. Adicione uma nova condição para seu provedor:
   ```python
   elif MODEL_PROVIDER == "anthropic":
       trading_model = LitellmModel(
           model="anthropic/claude-3-5-sonnet-20241022",
           api_key=os.getenv("ANTHROPIC_API_KEY")
       )
   ```
3. Atualize esta documentação

## Comparação de Desempenho

| Métrica | Cerebras gpt-oss-120b | Groq qwen3-32b | OpenAI gpt-5-mini |
|--------|----------------------|----------------|-------------------|
| Tamanho do Modelo | 120B parâmetros | 32B parâmetros | Desconhecido (mini) |
| Velocidade | ⚡⚡⚡ ~50ms/requisição | ⚡⚡ ~100ms/requisição | 🐌 ~500ms/requisição |
| Tokens/seg | 1800+ | 200-500 | 50-100 |
| Custo | $0,60/1M entrada + $0,60/1M saída | $0,05/1M tokens | $0,15/1M entrada + $0,60/1M saída |
| Qualidade | Excelente (120B) | Muito Bom (32B) | Excelente |
| Raciocínio | Melhor da categoria | Forte | Melhor da categoria |
| Disponibilidade | 99% uptime | 99% uptime | 99,9% uptime |
| **Ideal Para** | **Trading em tempo real** | Decisões rápidas | Crítico de precisão |

## Solução de Problemas

### Erro de Importação
```
ModuleNotFoundError: No module named 'agents.extensions.models.litellm_model'
```
**Solução**: Instale com suporte LiteLLM:
```bash
uv add openai-agents[litellm]
uv sync
```

### Erro de Chave de API
```
litellm.AuthenticationError: API key not found
```
**Solução**: Certifique-se de que a chave de API correta está definida no `.env`:
- Para OpenAI: `OPENAI_API_KEY=sk-...`
- Para Groq: `GROQ_API_KEY=gsk-...`

### Modelo Não Encontrado
```
litellm.exceptions.BadRequestError: model 'gpt-5-mini' not found
```
**Solução**: Verifique se o nome do modelo está correto e disponível. Se o nome do modelo mudar, atualize `agent.py` linha 53.

## Estimativa de Custos

### Custos Diários de Trading (Estimado)

**Suposições**:
- 375 ciclos de trading por dia (9:15 - 15:15, a cada minuto)
- 5 símbolos por ciclo
- ~2000 tokens por ciclo (análise + decisões)
- Total: 750.000 tokens/dia

**OpenAI (gpt-5-mini)**:
- Custo: ~$0,11/dia (~$3,30/mês)

**Groq (llama-3.3-70b)**:
- Custo: ~$0,04/dia (~$1,20/mês)

*Nota: Custos reais podem variar com base nas condições de mercado e complexidade das decisões.*
