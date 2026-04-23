"""
Ponto de entrada e orquestração do Agente de Trading Autônomo OpenAlgo.
Coordena dados de mercado, motor de trading, regras por indicadores e gerenciamento de estado (sem LLM).
"""
import sys
import io
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from colorama import Fore, Style, init
from dotenv import load_dotenv


def _configure_windows_console_utf8() -> None:
    """Evita UnicodeEncodeError (cp1252) ao imprimir caracteres Unicode no Windows."""
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOBase) and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


# Importar módulos modularizados
from config import (
    SYMBOLS,
    IST,
    MARKET_OPEN_HOUR,
    MARKET_OPEN_MINUTE,
    SQUARE_OFF_HOUR,
    SQUARE_OFF_MINUTE,
    DAILY_RESET_HOUR,
    DAILY_RESET_MINUTE,
    setup_openalgo_client,
)
from utils import setup_logging, get_current_time_in_timezone
from market_data import MarketDataClient
from trading_engine import TradingEngine
from ai_agent import AIAgent

_configure_windows_console_utf8()
# Inicializar colorama para compatibilidade Windows
init(autoreset=True)

# Configurar logger
logger = setup_logging()

# Carregar variáveis de ambiente
load_dotenv(override=True)

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

def initialize_system():
    """
    Inicializa todos os componentes do sistema de trading.

    Returns:
        Tupla (cliente_openalgo, market_client, trading_engine, ai_agent, trade_state).
    """
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[INICIALIZAÇÃO] Agente de Trading Autônomo OpenAlgo{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

    # Configurar cliente OpenAlgo
    client = setup_openalgo_client()
    print(f"{Fore.GREEN}[CLIENTE] OpenAlgo conectado em {os.getenv('OPENALGO_HOST', 'http://127.0.0.1:5000')}{Style.RESET_ALL}\n")
    
    # Inicializar estado de trades
    trade_state = {
        "daily_pnl": 0.0,
        "trade_counts": {symbol: 0 for symbol in SYMBOLS},
        "trade_history": [],
        "active_positions": {},
        "stop_loss_hit": False,
        "squared_off_today": False
    }
    
    # Inicializar clientes
    market_client = MarketDataClient(client)
    trading_engine = TradingEngine(client, trade_state)
    ai_agent = AIAgent()
    
    print(f"{Fore.GREEN}[SISTEMA] Todos os componentes inicializados com sucesso{Style.RESET_ALL}\n")

    return client, market_client, trading_engine, ai_agent, trade_state

# ============================================================================
# FUNÇÕES DE ORQUESTRAÇÃO DO CICLO DE TRADING
# ============================================================================

async def run_trading_cycle(market_client, trading_engine, ai_agent, trade_state):
    """
    Executar um ciclo completo de trading: buscar dados, analisar, decidir e executar.
    
    Args:
        market_client: Cliente de dados de mercado.
        trading_engine: Motor de execução de ordens.
        ai_agent: Agente de regras (indicadores + histórico).
        trade_state: Estado atual dos trades.
    """
    try:
        current_time = get_current_time_in_timezone(IST)
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[CICLO DE TRADING] Iniciado em {current_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # 1. Buscar todos os dados de mercado em paralelo
        print(f"{Fore.BLUE}[ETAPA 1] Buscando dados de mercado...{Style.RESET_ALL}")
        all_market_data = market_client.get_all_market_data()
        
        if all_market_data.get("status") != "success":
            print(f"{Fore.RED}[ERRO] Falha ao buscar dados de mercado{Style.RESET_ALL}")
            return
        
        # 2. Para cada símbolo, analisar e tomar decisão
        for symbol in SYMBOLS:
            symbol_data = all_market_data.get("data", {}).get(symbol, {})
            
            if "error" in symbol_data:
                print(f"{Fore.RED}[ERRO] Dados inválidos para {symbol}: {symbol_data['error']}{Style.RESET_ALL}")
                continue
            
            print(f"\n{Fore.YELLOW}[ANÁLISE] Processando {symbol}...{Style.RESET_ALL}")

            # 3. Sinais a partir de indicadores (sem LLM)
            sentiment_score, recommendation = ai_agent.analyze_market_sentiment(symbol_data)
            
            # 4. Analisar performance passada
            past_performance = ai_agent.analyze_past_trades(symbol, trade_state.get("trade_history", []))
            
            # 5. Verificar restrições de risco
            risk_analysis = trading_engine.check_risk_constraints(symbol, recommendation)
            
            # 6. Tomar decisão final
            final_action = ai_agent.decide_action(
                sentiment_score=sentiment_score,
                recommendation=recommendation,
                risk_analysis=risk_analysis,
                past_performance=past_performance
            )
            
            # 7. Executar ação se não for HOLD
            if final_action != "HOLD":
                # Calcular tamanho da posição
                ltp = symbol_data.get('ltp', 0)
                position_calc = trading_engine.calculate_position_size(symbol, ltp)
                
                if not position_calc.get("error"):
                    quantity = position_calc.get("quantity", 0)
                    
                    if quantity > 0:
                        # Executar ordem
                        order_result = trading_engine.place_order(symbol, final_action, quantity)
                        
                        if order_result.get("success"):
                            # Registrar no histórico
                            trade_state["trade_history"].append({
                                "symbol": symbol,
                                "action": final_action,
                                "quantity": quantity,
                                "price": ltp,
                                "timestamp": get_current_time_in_timezone(IST).isoformat(),
                                "reason": recommendation,
                                "sentiment_score": sentiment_score,
                                "pnl": 0  # Será atualizado quando a posição for fechada
                            })
        
        print(f"\n{Fore.GREEN}[CICLO] Ciclo de trading concluído{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}[ERRO NO CICLO] {str(e)}{Style.RESET_ALL}")
        logger.error(f"Erro no ciclo de trading: {e}", exc_info=True)

async def square_off_all_positions(trading_engine, trade_state):
    """
    Fechar todas as posições ativas no final do dia.
    
    Args:
        trading_engine: Motor de execução de ordens.
        trade_state: Estado atual dos trades.
    """
    try:
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[SQUARE-OFF] Fechando todas as posições...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
        
        result = trading_engine.square_off_all_positions()
        
        if result.get("success"):
            print(f"{Fore.GREEN}[SQUARE-OFF] ✓ {len(result.get('closed_positions', []))} posições fechadas{Style.RESET_ALL}")
            trade_state["squared_off_today"] = True
        else:
            print(f"{Fore.RED}[ERRO] Falha no square-off: {result.get('error')}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}[ERRO NO SQUARE-OFF] {str(e)}{Style.RESET_ALL}")
        logger.error(f"Erro no square-off: {e}", exc_info=True)

async def reset_daily_state(trading_engine, trade_state):
    """
    Resetar o estado diário para um novo dia de trading.
    
    Args:
        trading_engine: Motor de execução de ordens.
        trade_state: Estado atual dos trades.
    """
    try:
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[RESET DIÁRIO] Preparando para novo dia de trading{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        trading_engine.reset_daily_state()
        
        # Gerar insights de aprendizado (usando método estático - sem instância desnecessária)
        insights = AIAgent.generate_learning_insights_static(trade_state)
        print(f"{Fore.CYAN}[INSIGHTS] {insights}{Style.RESET_ALL}\n")
    
    except Exception as e:
        print(f"{Fore.RED}[ERRO NO RESET] {str(e)}{Style.RESET_ALL}")
        logger.error(f"Erro no reset diário: {e}", exc_info=True)

# ============================================================================
# AGENDAMENTO E LOOP PRINCIPAL
# ============================================================================

def schedule_jobs(scheduler, market_client, trading_engine, ai_agent, trade_state):
    """
    Agendar jobs recorrentes para o trading.
    
    Args:
        scheduler: Agendador APScheduler.
        market_client: Cliente de dados de mercado.
        trading_engine: Motor de execução de ordens.
        ai_agent: Agente de regras.
        trade_state: Estado dos trades.
    """
    # Ciclo a cada 5 min entre abertura (MARKET_OPEN_*) e square-off (SQUARE_OFF_*), fuso IST
    _now = datetime.now(IST)
    session_start = _now.replace(
        hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0
    )
    session_end = _now.replace(
        hour=SQUARE_OFF_HOUR, minute=SQUARE_OFF_MINUTE, second=0, microsecond=0
    )
    scheduler.add_job(
        run_trading_cycle,
        trigger='cron',
        hour=f'{MARKET_OPEN_HOUR}-{SQUARE_OFF_HOUR}',
        minute='*/5',
        start_date=session_start,
        end_date=session_end,
        args=[market_client, trading_engine, ai_agent, trade_state],
        name='Ciclo de Trading',
    )
    
    # Job para square-off às 15:15
    scheduler.add_job(
        square_off_all_positions,
        trigger='cron',
        hour=SQUARE_OFF_HOUR,
        minute=SQUARE_OFF_MINUTE,
        args=[trading_engine, trade_state],
        name='Square-Off Diário'
    )
    
    # Job para reset diário às 15:45
    scheduler.add_job(
        reset_daily_state,
        trigger='cron',
        hour=DAILY_RESET_HOUR,
        minute=DAILY_RESET_MINUTE,
        args=[trading_engine, trade_state],
        name='Reset Diário'
    )
    
    print(f"{Fore.GREEN}[AGENDAMENTO] Jobs agendados com sucesso{Style.RESET_ALL}")

async def main_async():
    """Função assíncrona principal."""
    # Inicializar sistema
    client, market_client, trading_engine, ai_agent, trade_state = initialize_system()
    
    # Criar scheduler assíncrono
    scheduler = AsyncIOScheduler(timezone=IST)
    
    # Agendar jobs
    schedule_jobs(scheduler, market_client, trading_engine, ai_agent, trade_state)
    
    # Iniciar scheduler
    scheduler.start()
    print(f"{Fore.GREEN}[SCHEDULER] Agendador iniciado - aguardando próximos jobs{Style.RESET_ALL}\n")
    
    # Manter o script rodando
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{Fore.YELLOW}[PARANDO] Agente encerrado pelo usuário{Style.RESET_ALL}")
        scheduler.shutdown()

def main():
    """Função de entrada principal."""
    print(f"\n{Fore.CYAN}╔{'═'*78}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{'Agente de Trading Autônomo OpenAlgo - Módulo Principal':^78}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═'*78}╝{Style.RESET_ALL}\n")
    
    try:
        # Rodar loop assíncrono
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[INTERRUPÇÃO] Programa encerrado{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERRO FATAL] {str(e)}{Style.RESET_ALL}")
        logger.critical(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
