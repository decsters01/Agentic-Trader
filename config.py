"""
Configurações centrais do Agente de Trading Autônomo OpenAlgo.
Lê parâmetros do ambiente (`.env`) e expõe limiares de trading e de decisão por indicadores.
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

# ============================================================================
# LIMIARES DE SINAIS (regras; ver indicator_signals.py e ai_agent.decide_action)
# ============================================================================
DEFAULT_SENTIMENT_THRESHOLD_BUY = 0.6
DEFAULT_SENTIMENT_THRESHOLD_SELL = 0.4

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
# LIMIARES DE DECISÃO
# ============================================================================
SENTIMENT_THRESHOLD_BUY = float(os.getenv("SENTIMENT_THRESHOLD_BUY", str(DEFAULT_SENTIMENT_THRESHOLD_BUY)))
SENTIMENT_THRESHOLD_SELL = float(os.getenv("SENTIMENT_THRESHOLD_SELL", str(DEFAULT_SENTIMENT_THRESHOLD_SELL)))

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
