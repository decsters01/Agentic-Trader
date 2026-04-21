"""
Funções utilitárias para o Agente de Trading.
Formatação de dados, cálculos técnicos, manipulação de tempo e logs.
"""
import logging
import numpy as np
import talib
import pytz
from datetime import datetime
from typing import Dict, Any, List, Optional
from colorama import Fore, Style

# Configurar logger
def setup_logging():
    """Configura o sistema de logs com arquivo e console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("trading_agent.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# CÁLCULOS TÉCNICOS
# ============================================================================

def calculate_technical_indicators(history_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula indicadores técnicos (RSI, MACD, EMA) a partir dos dados históricos.
    
    Args:
        history_data: Dicionário contendo arrays de preços 'close', 'high', 'low'.
        
    Returns:
        Dicionário com RSI atual, tendência MACD e tendência EMA.
    """
    try:
        close_prices = history_data['close'].values
        high_prices = history_data['high'].values
        low_prices = history_data['low'].values

        # Calcular RSI (14 períodos)
        rsi = talib.RSI(close_prices, timeperiod=14)
        
        # Calcular MACD
        macd, macd_signal, _ = talib.MACD(
            close_prices, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        
        # Calcular EMAs (20 e 50 períodos)
        ema_20 = talib.EMA(close_prices, timeperiod=20)
        ema_50 = talib.EMA(close_prices, timeperiod=50)

        # Extrair valores atuais (últimos válidos)
        rsi_current = round(float(rsi[~np.isnan(rsi)][-1]), 2) if len(rsi[~np.isnan(rsi)]) > 0 else 50.0
        
        macd_current = float(macd[~np.isnan(macd)][-1]) if len(macd[~np.isnan(macd)]) > 0 else 0
        macd_signal_current = float(macd_signal[~np.isnan(macd_signal)][-1]) if len(macd_signal[~np.isnan(macd_signal)]) > 0 else 0
        macd_trend = "bullish" if macd_current > macd_signal_current else "bearish"

        ema_20_current = float(ema_20[~np.isnan(ema_20)][-1]) if len(ema_20[~np.isnan(ema_20)]) > 0 else 0
        ema_50_current = float(ema_50[~np.isnan(ema_50)][-1]) if len(ema_50[~np.isnan(ema_50)]) > 0 else 0
        ema_trend = "bullish" if ema_20_current > ema_50_current else "bearish"

        return {
            "rsi": rsi_current,
            "macd_trend": macd_trend,
            "ema_trend": ema_trend,
            "ema_20": ema_20_current,
            "ema_50": ema_50_current
        }
    except Exception as e:
        logger.error(f"Erro ao calcular indicadores técnicos: {e}")
        return {
            "rsi": 50.0,
            "macd_trend": "neutral",
            "ema_trend": "neutral",
            "ema_20": 0,
            "ema_50": 0
        }

def calculate_bid_ask_ratio(depth_data: Dict[str, Any]) -> float:
    """
    Calcula a razão entre quantidades de compra (bids) e venda (asks).
    
    Args:
        depth_data: Dados de profundidade de mercado contendo 'bids' e 'asks'.
        
    Returns:
        Razão bid/ask arredondada em 2 casas decimais.
    """
    try:
        total_bid = sum([b["quantity"] for b in depth_data.get("bids", [])])
        total_ask = sum([a["quantity"] for a in depth_data.get("asks", [])])
        return round(total_bid / total_ask, 2) if total_ask > 0 else 0.0
    except Exception as e:
        logger.warning(f"Erro ao calcular razão bid/ask: {e}")
        return 0.0

# ============================================================================
# MANIPULAÇÃO DE TEMPO E FUSO HORÁRIO
# ============================================================================

def get_current_time_in_timezone(timezone_str: str = 'Asia/Kolkata') -> datetime:
    """
    Retorna a hora atual no fuso horário especificado.
    
    Args:
        timezone_str: String do fuso horário (ex: 'Asia/Kolkata', 'America/New_York').
        
    Returns:
        Objeto datetime com a hora atual no fuso especificado.
    """
    tz = pytz.timezone(timezone_str)
    return datetime.now(tz)

def is_market_open(current_time: datetime, open_hour: int = 9, open_minute: int = 15, 
                   close_hour: int = 15, close_minute: int = 15) -> bool:
    """
    Verifica se o mercado está aberto com base no horário atual.
    
    Args:
        current_time: Horário atual (datetime).
        open_hour: Hora de abertura do mercado.
        open_minute: Minuto de abertura do mercado.
        close_hour: Hora de fechamento do mercado.
        close_minute: Minuto de fechamento do mercado.
        
    Returns:
        True se o mercado estiver aberto, False caso contrário.
    """
    current_minutes = current_time.hour * 60 + current_time.minute
    open_minutes = open_hour * 60 + open_minute
    close_minutes = close_hour * 60 + close_minute
    
    return open_minutes <= current_minutes <= close_minutes

def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formata um objeto datetime para string.
    
    Args:
        dt: Objeto datetime a ser formatado.
        format_string: Formato da string de saída.
        
    Returns:
        String formatada com a data/hora.
    """
    return dt.strftime(format_string)

# ============================================================================
# FORMATAÇÃO E UTILITÁRIOS GERAIS
# ============================================================================

def format_currency(value: float, currency_symbol: str = "₹") -> str:
    """
    Formata um valor numérico como moeda.
    
    Args:
        value: Valor numérico a ser formatado.
        currency_symbol: Símbolo da moeda (padrão: Rupia Indiana).
        
    Returns:
        String formatada com o valor monetário.
    """
    return f"{currency_symbol}{value:,.2f}"

def format_number(value: float, decimals: int = 2) -> str:
    """
    Formata um número com casas decimais específicas.
    
    Args:
        value: Valor numérico a ser formatado.
        decimals: Número de casas decimais.
        
    Returns:
        String formatada com o número.
    """
    return f"{value:.{decimals}f}"

def print_colored_message(message: str, color: str = Fore.WHITE):
    """
    Imprime uma mensagem colorida no console.
    
    Args:
        message: Mensagem a ser impressa.
        color: Cor da mensagem (usando constantes da Colorama).
    """
    print(f"{color}{message}{Style.RESET_ALL}", flush=True)

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """
    Obtém um valor de um dicionário de forma segura, retornando um padrão se a chave não existir.
    
    Args:
        data: Dicionário de onde obter o valor.
        key: Chave a ser buscada.
        default: Valor padrão caso a chave não exista.
        
    Returns:
        O valor associado à chave ou o valor padrão.
    """
    return data.get(key, default) if isinstance(data, dict) else default
