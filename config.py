"""
Configurações centrais do Agente de Trading Autônomo OpenAlgo.
Contém chaves de API, parâmetros de trading, limiares de decisão e configurações de modelo.
"""
import os
from dotenv import load_dotenv
from colorama import Fore, Style

# Carregar variáveis de ambiente
load_dotenv(override=True)

# ============================================================================
# CONFIGURAÇÃO DO MODELO (Agnóstico ao Modelo - OpenAI, Groq, Cerebras ou Custom)
# ============================================================================

# Escolher provedor do modelo: "cerebras", "groq", "openai" ou "custom"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()

def setup_model():
    """
    Configura e retorna o modelo de IA baseado nas variáveis de ambiente.
    Retorna uma tupla (modelo, nome_do_modelo).
    """
    from agents.extensions.models.litellm_model import LitellmModel

    if MODEL_PROVIDER == "cerebras":
        # Configuração Cerebras (inferência ULTRA-RÁPIDA, excelente para trading em tempo real)
        # gpt-oss-120b é o modelo mais rápido do Cerebras (1800+ tokens/seg)
        model_name = os.getenv("CEREBRAS_MODEL", "cerebras/gpt-oss-120b")
        model = LitellmModel(
            model=model_name,
            api_key=os.getenv("CEREBRAS_API_KEY")
        )
        print(f"{Fore.CYAN}[MODELO] Usando Cerebras ({model_name}) - ULTRA-RÁPIDO (1800+ tokens/seg){Style.RESET_ALL}")

    elif MODEL_PROVIDER == "groq":
        # Configuração Groq (inferência rápida, custo-benefício)
        model_name = os.getenv("GROQ_MODEL", "groq/qwen/qwen3-32b")
        model = LitellmModel(
            model=model_name,
            api_key=os.getenv("GROQ_API_KEY")
        )
        print(f"{Fore.CYAN}[MODELO] Usando Groq ({model_name}){Style.RESET_ALL}")

    elif MODEL_PROVIDER == "custom":
        # Configuração de Modelo Customizado (usuários avançados)
        model_name = os.getenv("CUSTOM_MODEL", "openai/gpt-4o-mini")
        api_key = os.getenv("CUSTOM_API_KEY", os.getenv("OPENAI_API_KEY"))
        api_base = os.getenv("CUSTOM_API_BASE", None)

        # Definir API base via variável de ambiente se fornecida
        if api_base:
            # Extrair nome do provedor do modelo (ex: "anthropic" de "anthropic/claude-3")
            provider = model_name.split("/")[0].upper()
            os.environ[f"{provider}_API_BASE"] = api_base

        model = LitellmModel(
            model=model_name,
            api_key=api_key
        )
        print(f"{Fore.CYAN}[MODELO] Usando Custom ({model_name}){Style.RESET_ALL}")

    else:
        # Configuração OpenAI (Padrão - Alta qualidade, confiável)
        model_name = os.getenv("OPENAI_MODEL", "openai/gpt-5-mini")
        model = LitellmModel(
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        print(f"{Fore.CYAN}[MODELO] Usando OpenAI ({model_name}){Style.RESET_ALL}")

    return model, model_name

# Configurar cliente OpenAlgo
def setup_openalgo_client():
    """
    Inicializa e retorna o cliente da API OpenAlgo.
    """
    from openalgo import api
    client = api(
        api_key=os.getenv("OPENALGO_API_KEY"),
        host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000")
    )
    return client

# ============================================================================
# PARÂMETROS DE TRADING
# ============================================================================
SYMBOL = os.getenv("TRADING_SYMBOL", "AAPL")  # Símbolo para operar
TIMEFRAME = os.getenv("TRADING_TIMEFRAME", "1Min")  # Padrão Alpaca: 1Min, 5Min, 15Min, 1H, 1D
POSITION_SIZE_USD = float(os.getenv("POSITION_SIZE_USD", "50"))  # Valor em dólares por operação
MAX_POSITION_SIZE_USD = float(os.getenv("MAX_POSITION_SIZE_USD", "500"))  # Tamanho máximo total da posição em dólares
STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", "0.98"))  # Stop Loss: 2%
TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", "1.03"))  # Take Profit: 3%

# ============================================================================
# LIMIARES DE DECISÃO E IA
# ============================================================================
SENTIMENT_THRESHOLD_BUY = float(os.getenv("SENTIMENT_THRESHOLD_BUY", "0.6"))  # Limiar de sentimento para compra
SENTIMENT_THRESHOLD_SELL = float(os.getenv("SENTIMENT_THRESHOLD_SELL", "0.4"))  # Limiar de sentimento para venda
VOLATILITY_THRESHOLD = float(os.getenv("VOLATILITY_THRESHOLD", "0.02"))  # Limiar de volatilidade para pausar trading
TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.1"))  # Determina a aleatoriedade da resposta da IA

# ============================================================================
# CONFIGURAÇÕES DE AGENDAMENTO E FUSO HORÁRIO
# ============================================================================
TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "America/New_York"))  # Fuso horário do mercado
