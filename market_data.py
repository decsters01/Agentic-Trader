"""
Módulo de dados de mercado para o Agente de Trading.
Responsável por buscar cotações, profundidade e dados históricos via API OpenAlgo.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import time
import threading
from colorama import Fore, Style

# Importar configurações e utilitários
from config import SYMBOLS, EXCHANGE, TIMEZONE
from utils import calculate_technical_indicators, calculate_bid_ask_ratio, get_current_time_in_timezone, logger


class MarketDataClient:
    """Cliente para obter dados de mercado da API OpenAlgo."""
    
    def __init__(self, client):
        """
        Inicializa o cliente de dados de mercado.
        
        Args:
            client: Instância do cliente da API OpenAlgo.
        """
        self.client = client
    
    def get_all_market_data(self) -> Dict[str, Any]:
        """
        Buscar TODOS os dados de mercado (cotações, profundidade, histórico) para TODOS os símbolos com rate limiting.
        
        Usa threading para buscar todos os símbolos em paralelo respeitando o limite de 10 req/seg.
        Muito mais rápido que chamadas sequenciais.
        
        Returns:
            Dicionário contendo status, dados de todos os símbolos e tempo decorrido.
        """
        def fetch_symbol_data(symbol: str, results: dict, index: int):
            """Buscar todos os dados para um símbolo (roda em thread separada)."""
            try:
                # Delay de rate limiting baseado no índice do símbolo
                time.sleep(index * 0.2)  # Escalonar inícios em 0.2s

                # Buscar cotações
                quotes_response = self.client.quotes(symbol=symbol, exchange=EXCHANGE)
                quotes_data = quotes_response.get("data", {}) if quotes_response.get("status") == "success" else {}

                time.sleep(0.15)  # Delay de rate limit

                # Buscar profundidade
                depth_response = self.client.depth(symbol=symbol, exchange=EXCHANGE)
                depth_data = depth_response.get("data", {}) if depth_response.get("status") == "success" else {}

                # Calcular razão bid/ask
                bid_ask_ratio = calculate_bid_ask_ratio(depth_data)

                time.sleep(0.15)  # Delay de rate limit

                # Buscar dados históricos
                end_date = get_current_time_in_timezone(TIMEZONE).strftime("%Y-%m-%d")
                start_date = (get_current_time_in_timezone(TIMEZONE) - timedelta(days=3)).strftime("%Y-%m-%d")
                history_response = self.client.history(
                    symbol=symbol, 
                    exchange=EXCHANGE, 
                    interval="5m", 
                    start_date=start_date, 
                    end_date=end_date
                )

                # Calcular indicadores técnicos
                if isinstance(history_response, dict) and history_response.get("status") == "error":
                    rsi_current = 50.0
                    macd_trend = "neutral"
                    ema_trend = "neutral"
                else:
                    indicators = calculate_technical_indicators(history_response)
                    rsi_current = indicators["rsi"]
                    macd_trend = indicators["macd_trend"]
                    ema_trend = indicators["ema_trend"]

                results[symbol] = {
                    "symbol": symbol,
                    "ltp": quotes_data.get("ltp", 0),
                    "volume": quotes_data.get("volume", 0),
                    "bid_ask_ratio": bid_ask_ratio,
                    "rsi": rsi_current,
                    "macd_trend": macd_trend,
                    "ema_trend": ema_trend
                }
            except Exception as e:
                results[symbol] = {"symbol": symbol, "error": str(e)}

        # Buscar todos os símbolos usando threads (sem conflito com event loop asyncio)
        print(f"{Fore.BLUE}[BUSCA EM LOTE] Buscando TODOS os dados de mercado ({len(SYMBOLS)} símbolos em paralelo)...{Style.RESET_ALL}", flush=True)
        start_time = time.time()

        results = {}
        threads = []

        # Criar e iniciar threads
        for i, symbol in enumerate(SYMBOLS):
            thread = threading.Thread(target=fetch_symbol_data, args=(symbol, results, i))
            thread.start()
            threads.append(thread)

        # Aguardar todas as threads completarem
        for thread in threads:
            thread.join()

        elapsed = time.time() - start_time
        print(f"{Fore.GREEN}[BUSCA EM LOTE] ✓ Todos os dados buscados em {elapsed:.1f}s ({len(SYMBOLS) * 3} chamadas API){Style.RESET_ALL}", flush=True)

        return {"status": "success", "data": results, "elapsed_seconds": round(elapsed, 1)}

    def get_market_quotes(self, symbol: str) -> Dict[str, Any]:
        """
        Obter cotações atuais de mercado para um símbolo.
        
        Args:
            symbol: Símbolo do ativo para buscar cotações.
            
        Returns:
            Dicionário com dados de cotação ou erro.
        """
        try:
            print(f"{Fore.BLUE}[BUSCANDO] Buscando cotações de mercado para {symbol}...{Style.RESET_ALL}", flush=True)
            response = self.client.quotes(symbol=symbol, exchange=EXCHANGE)
            if response.get("status") == "success":
                data = response["data"]
                print(f"{Fore.BLUE}[DADOS] {symbol} Cotação: LTP={data['ltp']}, Volume={data['volume']:,}{Style.RESET_ALL}", flush=True)
                return {
                    "symbol": symbol,
                    "ltp": data["ltp"],
                    "open": data["open"],
                    "high": data["high"],
                    "low": data["low"],
                    "volume": data["volume"],
                    "prev_close": data["prev_close"]
                }
            print(f"{Fore.RED}[ERRO] Falha ao buscar cotações para {symbol}{Style.RESET_ALL}", flush=True)
            return {"error": response.get("message", "Falha ao buscar cotações")}
        except Exception as e:
            print(f"{Fore.RED}[ERRO] {str(e)}{Style.RESET_ALL}", flush=True)
            return {"error": str(e)}

    def get_market_depth(self, symbol: str) -> Dict[str, Any]:
        """
        Obter profundidade de mercado (níveis de bid/ask) para um símbolo.
        
        Args:
            symbol: Símbolo do ativo para buscar profundidade.
            
        Returns:
            Dicionário com dados de profundidade ou erro.
        """
        try:
            print(f"{Fore.BLUE}[BUSCANDO] Buscando profundidade de mercado para {symbol}...{Style.RESET_ALL}", flush=True)
            response = self.client.depth(symbol=symbol, exchange=EXCHANGE)
            if response.get("status") == "success":
                data = response["data"]
                total_bid = sum([b["quantity"] for b in data["bids"]])
                total_ask = sum([a["quantity"] for a in data["asks"]])
                bid_ask_ratio = total_bid / total_ask if total_ask > 0 else 0

                print(f"{Fore.BLUE}[DADOS] {symbol} Profundidade: Bids={total_bid:,}, Asks={total_ask:,}, Ratio={bid_ask_ratio:.2f}{Style.RESET_ALL}", flush=True)

                return {
                    "symbol": symbol,
                    "total_bid_qty": total_bid,
                    "total_ask_qty": total_ask,
                    "bid_ask_ratio": round(bid_ask_ratio, 2),
                    "best_bid": data["bids"][0]["price"] if data["bids"] else 0,
                    "best_ask": data["asks"][0]["price"] if data["asks"] else 0
                }
            print(f"{Fore.RED}[ERRO] Falha ao buscar profundidade para {symbol}{Style.RESET_ALL}", flush=True)
            return {"error": response.get("message", "Falha ao buscar profundidade")}
        except Exception as e:
            print(f"{Fore.RED}[ERRO] {str(e)}{Style.RESET_ALL}", flush=True)
            return {"error": str(e)}

    def get_historical_data(self, symbol: str, lookback_bars: int = 5) -> Dict[str, Any]:
        """
        Obter dados históricos de 5 minutos e calcular indicadores técnicos TA-Lib para os últimos N períodos.
        
        Args:
            symbol: Símbolo da ação para buscar.
            lookback_bars: Número de períodos recentes para retornar (padrão: 5, mín: 1, máx: 20).
            
        Returns:
            Dicionário com dados históricos e indicadores técnicos calculados.
        """
        try:
            # Validar lookback_bars (reduzido máx para velocidade)
            lookback_bars = max(1, min(20, lookback_bars))

            print(f"{Fore.BLUE}[BUSCANDO] Buscando dados históricos para {symbol} (últimos {lookback_bars} períodos)...{Style.RESET_ALL}", flush=True)
            end_date = get_current_time_in_timezone(TIMEZONE).strftime("%Y-%m-%d")
            start_date = (get_current_time_in_timezone(TIMEZONE) - timedelta(days=3)).strftime("%Y-%m-%d")

            response = self.client.history(
                symbol=symbol,
                exchange=EXCHANGE,
                interval="5m",
                start_date=start_date,
                end_date=end_date
            )

            if isinstance(response, dict) and response.get("status") == "error":
                print(f"{Fore.RED}[ERRO] Falha ao buscar histórico para {symbol}{Style.RESET_ALL}", flush=True)
                return {"error": response.get("message")}

            # Calcular indicadores técnicos usando a função utilitária
            indicators = calculate_technical_indicators(response)
            
            # Extrair últimos N períodos de preços de fechamento
            close_bars = [round(float(x), 2) for x in response['close'].values[-lookback_bars:]]
            current_price = close_bars[-1] if close_bars else 0.0

            # Volatilidade recente e volume médio
            recent_data = response.tail(12)  # Última hora
            volatility = recent_data['close'].std()
            avg_volume = recent_data['volume'].mean()

            print(f"{Fore.BLUE}[DADOS] {symbol} Indicadores TA (últimos {lookback_bars} períodos): RSI={indicators['rsi']}, MACD={indicators['macd_trend']}, EMA={indicators['ema_trend']}{Style.RESET_ALL}", flush=True)

            return {
                "symbol": symbol,
                "current_price": current_price,
                "close_bars": close_bars,
                "indicators": indicators,
                "volatility": round(volatility, 2),
                "avg_volume": round(avg_volume, 2),
                "lookback_bars": lookback_bars
            }
        except Exception as e:
            print(f"{Fore.RED}[ERRO] {str(e)}{Style.RESET_ALL}", flush=True)
            return {"error": str(e)}
