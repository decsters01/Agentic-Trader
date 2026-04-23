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

# Constantes nomeadas para valores mágicos
DEFAULT_MODEL_PROVIDER = "openai"
DEFAULT_CEREBRAS_MODEL = "cerebras/gpt-oss-120b"
DEFAULT_GROQ_MODEL = "groq/qwen/qwen3-32b"
DEFAULT_CUSTOM_MODEL = "openai/gpt-4o-mini"
DEFAULT_OPENAI_MODEL = "openai/gpt-5-mini"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_SENTIMENT_THRESHOLD_BUY = 0.6
DEFAULT_SENTIMENT_THRESHOLD_SELL = 0.4
DEFAULT_VOLATILITY_THRESHOLD = 0.02

# Escolher provedor do modelo: "cerebras", "groq", "openai" ou "custom"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", DEFAULT_MODEL_PROVIDER).lower()

def setup_model():
    """
    Configura e retorna o modelo de IA baseado nas variáveis de ambiente.
    Retorna uma tupla (modelo, nome_do_modelo).
    """
    from agents.extensions.models.litellm_model import LitellmModel

    if MODEL_PROVIDER == "cerebras":
        # Configuração Cerebras (inferência ULTRA-RÁPIDA, excelente para trading em tempo real)
        # gpt-oss-120b é o modelo mais rápido do Cerebras (1800+ tokens/seg)
        model_name = os.getenv("CEREBRAS_MODEL", DEFAULT_CEREBRAS_MODEL)
        model = LitellmModel(
            model=model_name,
            api_key=os.getenv("CEREBRAS_API_KEY")
        )
        print(f"{Fore.CYAN}[MODELO] Usando Cerebras ({model_name}) - ULTRA-RÁPIDO (1800+ tokens/seg){Style.RESET_ALL}")

    elif MODEL_PROVIDER == "groq":
        # Configuração Groq (inferência rápida, custo-benefício)
        model_name = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        model = LitellmModel(
            model=model_name,
            api_key=os.getenv("GROQ_API_KEY")
        )
        print(f"{Fore.CYAN}[MODELO] Usando Groq ({model_name}){Style.RESET_ALL}")

    elif MODEL_PROVIDER == "custom":
        # Configuração de Modelo Customizado (usuários avançados)
        model_name = os.getenv("CUSTOM_MODEL", DEFAULT_CUSTOM_MODEL)
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
        model_name = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
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
# Constantes nomeadas para valores mágicos de trading
DEFAULT_SYMBOL = "AAPL"
DEFAULT_TIMEFRAME = "1Min"
DEFAULT_POSITION_SIZE_USD = 50.0
DEFAULT_MAX_POSITION_SIZE_USD = 500.0
DEFAULT_STOP_LOSS_PERCENTAGE = 0.98  # Stop Loss: 2%
DEFAULT_TAKE_PROFIT_PERCENTAGE = 1.03  # Take Profit: 3%

SYMBOL = os.getenv("TRADING_SYMBOL", DEFAULT_SYMBOL)  # Símbolo para operar
TIMEFRAME = os.getenv("TRADING_TIMEFRAME", DEFAULT_TIMEFRAME)  # Padrão Alpaca: 1Min, 5Min, 15Min, 1H, 1D
POSITION_SIZE_USD = float(os.getenv("POSITION_SIZE_USD", str(DEFAULT_POSITION_SIZE_USD)))  # Valor em dólares por operação
MAX_POSITION_SIZE_USD = float(os.getenv("MAX_POSITION_SIZE_USD", str(DEFAULT_MAX_POSITION_SIZE_USD)))  # Tamanho máximo total da posição em dólares
STOP_LOSS_PERCENTAGE = float(os.getenv("STOP_LOSS_PERCENTAGE", str(DEFAULT_STOP_LOSS_PERCENTAGE)))  # Stop Loss: 2%
TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", str(DEFAULT_TAKE_PROFIT_PERCENTAGE)))  # Take Profit: 3%

# ============================================================================
# LIMIARES DE DECISÃO E IA
# ============================================================================
SENTIMENT_THRESHOLD_BUY = float(os.getenv("SENTIMENT_THRESHOLD_BUY", str(DEFAULT_SENTIMENT_THRESHOLD_BUY)))  # Limiar de sentimento para compra
SENTIMENT_THRESHOLD_SELL = float(os.getenv("SENTIMENT_THRESHOLD_SELL", str(DEFAULT_SENTIMENT_THRESHOLD_SELL)))  # Limiar de sentimento para venda
VOLATILITY_THRESHOLD = float(os.getenv("VOLATILITY_THRESHOLD", str(DEFAULT_VOLATILITY_THRESHOLD)))  # Limiar de volatilidade para pausar trading
TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", str(DEFAULT_TEMPERATURE)))  # Determina a aleatoriedade da resposta da IA

# ============================================================================
# CONFIGURAÇÕES DE AGENDAMENTO E FUSO HORÁRIO
# ============================================================================
import pytz  # Import necessário para timezone

TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "America/New_York"))  # Fuso horário do mercado
IST = pytz.timezone("Asia/Kolkata")  # Horário padrão da Índia (NSE)
MARKET_OPEN_HOUR = int(os.getenv("MARKET_OPEN_HOUR", "9"))  # Hora de abertura do mercado
MARKET_OPEN_MINUTE = int(os.getenv("MARKET_OPEN_MINUTE", "15"))  # Minuto de abertura do mercado
SQUARE_OFF_HOUR = int(os.getenv("SQUARE_OFF_HOUR", "15"))  # Hora do square-off
SQUARE_OFF_MINUTE = int(os.getenv("SQUARE_OFF_MINUTE", "15"))  # Minuto do square-off
DAILY_RESET_HOUR = int(os.getenv("DAILY_RESET_HOUR", "15"))  # Hora do reset diário
DAILY_RESET_MINUTE = int(os.getenv("DAILY_RESET_MINUTE", "45"))  # Minuto do reset diário

# Parâmetros de trading específicos para NSE
SYMBOLS = os.getenv("TRADING_SYMBOLS", "ICICIBANK,WIPRO").split(",")  # Lista de símbolos para operar
EXCHANGE = os.getenv("TRADING_EXCHANGE", "NSE")  # Bolsa de valores
PRODUCT = os.getenv("TRADING_PRODUCT", "MIS")  # Tipo de produto (MIS, CNC, etc.)
MAX_INVESTMENT_PER_TRADE = float(os.getenv("MAX_INVESTMENT_PER_TRADE", "10000"))  # Max investimento por trade
DAILY_STOP_LOSS = float(os.getenv("DAILY_STOP_LOSS", "-5000"))  # Stop loss diário
MAX_TRADES_PER_SYMBOL = int(os.getenv("MAX_TRADES_PER_SYMBOL", "5"))  # Max trades por símbolo por dia
