"""
Módulo de motor de trading para o Agente de Trading.
Responsável por executar ordens, gerenciar posições e aplicar regras de risco.
"""
from typing import Dict, Any, List
import json
from colorama import Fore, Style

# Importar configurações
from config import (
    SYMBOLS, MAX_INVESTMENT_PER_TRADE, DAILY_STOP_LOSS, 
    MAX_TRADES_PER_SYMBOL, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE
)


class TradingEngine:
    """Motor de execução de ordens e gerenciamento de posições."""
    
    def __init__(self, client, initial_trade_state: Dict[str, Any]):
        """
        Inicializa o motor de trading.
        
        Args:
            client: Instância do cliente da API OpenAlgo.
            initial_trade_state: Estado inicial do gerenciamento de trades.
        """
        self.client = client
        self.trade_state = initial_trade_state
    
    def check_risk_constraints(self, symbol: str, action: str) -> Dict[str, Any]:
        """
        Verificar todas as restrições de risco antes de permitir um trade.
        
        Args:
            symbol: Símbolo do ativo para verificar.
            action: Ação proposta ("BUY" ou "SELL").
            
        Returns:
            Dicionário indicando se o trade é permitido e o motivo.
        """
        # Verificar stop loss diário atingido
        if self.trade_state["stop_loss_hit"]:
            return {
                "allowed": False,
                "reason": "Stop loss diário atingido. Trading pausado até reset."
            }
        
        # Verificar se já fez square-off hoje
        if self.trade_state["squared_off_today"] and action == "BUY":
            return {
                "allowed": False,
                "reason": "Já realizou square-off hoje. Nenhuma nova compra permitida."
            }
        
        # Verificar limite de trades por símbolo
        if self.trade_state["trade_counts"].get(symbol, 0) >= MAX_TRADES_PER_SYMBOL:
            return {
                "allowed": False,
                "reason": f"Máximo de {MAX_TRADES_PER_SYMBOL} trades atingido para {symbol} hoje."
            }
        
        # Verificar limite de investimento por trade
        current_position = self.trade_state["active_positions"].get(symbol, {"quantity": 0, "avg_price": 0})
        if action == "BUY":
            potential_investment = current_position.get("quantity", 0) * current_position.get("avg_price", 0) + MAX_INVESTMENT_PER_TRADE
            if potential_investment > MAX_INVESTMENT_PER_TRADE * 2:  # Limite flexível de 2x
                return {
                    "allowed": False,
                    "reason": f"Limite de exposição para {symbol} seria excedido."
                }
        
        return {"allowed": True, "reason": "Trade permitido dentro das regras de risco"}
    
    def check_all_risk_constraints(self, trades: str) -> Dict[str, Any]:
        """
        Validar múltiplos trades de uma vez (verificação de risco em lote).
        
        Args:
            trades: String JSON com formato: [{"symbol": "ICICIBANK", "action": "BUY"}, ...]
            
        Returns:
            Resultados da verificação de risco para todos os trades.
        """
        try:
            trades_list = json.loads(trades)

            if not isinstance(trades_list, list):
                return {"success": False, "error": "trades deve ser um array JSON"}

            print(f"{Fore.YELLOW}[VERIFICAÇÃO DE RISCO EM LOTE] Verificando {len(trades_list)} trades...{Style.RESET_ALL}", flush=True)

            results = []
            for trade in trades_list:
                symbol = trade["symbol"]
                action = trade["action"]
                risk_result = self.check_risk_constraints(symbol, action)
                results.append({
                    "symbol": symbol,
                    "action": action,
                    "allowed": risk_result.get("allowed", False),
                    "reason": risk_result.get("reason", "")
                })

            allowed_count = sum(1 for r in results if r["allowed"])
            print(f"{Fore.GREEN}[VERIFICAÇÃO DE RISCO EM LOTE] ✓ {allowed_count}/{len(trades_list)} trades permitidos{Style.RESET_ALL}", flush=True)

            return {"success": True, "results": results}

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON inválido: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_position_size(self, symbol: str, ltp: float, max_investment: float = None) -> Dict[str, Any]:
        """
        Calcular a quantidade correta de ações para comprar baseado no LTP e investimento máximo por trade.
        
        Esta ferramenta DEVE ser usada antes de colocar qualquer ordem para garantir o dimensionamento correto da posição.
        
        Args:
            symbol: Símbolo da ação (ex: "ICICIBANK", "WIPRO").
            ltp: Last Traded Price (preço atual de mercado).
            max_investment: Investimento máximo por trade em R$ (padrão: MAX_INVESTMENT_PER_TRADE).
            
        Returns:
            Dicionário com detalhes de quantidade e investimento calculados.
        """
        if max_investment is None:
            max_investment = MAX_INVESTMENT_PER_TRADE
            
        try:
            quantity = int(max_investment / ltp) if ltp > 0 else 0
            actual_investment = quantity * ltp
            
            print(f"{Fore.CYAN}[DIMENSIONAMENTO] {symbol}: Qty={quantity}, Investimento=R${actual_investment:.2f}{Style.RESET_ALL}", flush=True)
            
            return {
                "symbol": symbol,
                "ltp": round(ltp, 2),
                "quantity": quantity,
                "actual_investment": round(actual_investment, 2),
                "max_investment_limit": max_investment
            }
        except Exception as e:
            print(f"{Fore.RED}[ERRO] Falha ao calcular tamanho da posição: {str(e)}{Style.RESET_ALL}", flush=True)
            return {"error": str(e)}
    
    def calculate_all_position_sizes(self, positions: str) -> Dict[str, Any]:
        """
        Calcular tamanhos de posição para múltiplos símbolos de uma vez (cálculo em lote).
        
        Args:
            positions: String JSON com formato: [{"symbol": "ICICIBANK", "ltp": 1350.0}, ...]
            
        Returns:
            Cálculos de tamanho de posição para todos os símbolos.
        """
        try:
            positions_list = json.loads(positions)

            if not isinstance(positions_list, list):
                return {"success": False, "error": "positions deve ser um array JSON"}

            print(f"{Fore.CYAN}[CÁLCULO EM LOTE] Calculando tamanhos para {len(positions_list)} símbolos...{Style.RESET_ALL}", flush=True)

            results = []
            for pos in positions_list:
                symbol = pos["symbol"]
                ltp = pos["ltp"]
                max_investment = pos.get("max_investment", MAX_INVESTMENT_PER_TRADE)

                quantity = int(max_investment / ltp) if ltp > 0 else 0
                actual_investment = quantity * ltp

                results.append({
                    "symbol": symbol,
                    "ltp": round(ltp, 2),
                    "quantity": quantity,
                    "actual_investment": round(actual_investment, 2)
                })

                print(f"{Fore.CYAN}  {symbol}: Qty={quantity}, Investimento=R${actual_investment:.2f}{Style.RESET_ALL}", flush=True)

            return {"success": True, "results": results}

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON inválido: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def place_order(self, symbol: str, action: str, quantity: int, price: float = None) -> Dict[str, Any]:
        """
        Executar uma ordem de compra ou venda.
        
        Args:
            symbol: Símbolo do ativo.
            action: "BUY" ou "SELL".
            quantity: Quantidade de ações.
            price: Preço limite (opcional, se None usa ordem de mercado).
            
        Returns:
            Dicionário com resultado da ordem executada.
        """
        try:
            # Verificar restrições de risco primeiro
            risk_check = self.check_risk_constraints(symbol, action)
            if not risk_check["allowed"]:
                print(f"{Fore.RED}[ORDEM BLOQUEADA] {risk_check['reason']}{Style.RESET_ALL}", flush=True)
                return {"success": False, "error": risk_check["reason"]}
            
            # Determinar tipo de ordem
            order_type = "LIMIT" if price else "MARKET"
            
            print(f"{Fore.GREEN}[ENVIANDO ORDEM] {action} {quantity} {symbol} @ {price if price else 'MERCADO'}{Style.RESET_ALL}", flush=True)
            
            # Simulação de envio de ordem (substituir pela chamada real da API)
            # order_response = self.client.order(...)
            
            # Atualizar estado do trade
            self.trade_state["trade_counts"][symbol] = self.trade_state["trade_counts"].get(symbol, 0) + 1
            
            if action == "BUY":
                # Atualizar posição ativa
                current_pos = self.trade_state["active_positions"].get(symbol, {"quantity": 0, "avg_price": 0})
                new_quantity = current_pos.get("quantity", 0) + quantity
                new_avg_price = ((current_pos.get("quantity", 0) * current_pos.get("avg_price", 0)) + (quantity * price)) / new_quantity if new_quantity > 0 else 0
                
                self.trade_state["active_positions"][symbol] = {
                    "quantity": new_quantity,
                    "avg_price": new_avg_price
                }
            elif action == "SELL":
                # Reduzir ou fechar posição
                if symbol in self.trade_state["active_positions"]:
                    current_pos = self.trade_state["active_positions"][symbol]
                    new_quantity = current_pos.get("quantity", 0) - quantity
                    
                    if new_quantity <= 0:
                        del self.trade_state["active_positions"][symbol]
                    else:
                        current_pos["quantity"] = new_quantity
            
            print(f"{Fore.GREEN}[ORDEM EXECUTADA] ✓ {action} {quantity} {symbol}{Style.RESET_ALL}", flush=True)
            
            return {
                "success": True,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": price,
                "order_type": order_type
            }
            
        except Exception as e:
            print(f"{Fore.RED}[ERRO NA ORDEM] {str(e)}{Style.RESET_ALL}", flush=True)
            return {"success": False, "error": str(e)}
    
    def update_daily_pnl(self, pnl: float):
        """
        Atualizar o P&L (Lucro/Prejuízo) diário.
        
        Args:
            pnl: Valor do lucro ou prejuízo do trade.
        """
        self.trade_state["daily_pnl"] += pnl
        
        # Verificar se atingiu stop loss diário
        if self.trade_state["daily_pnl"] <= DAILY_STOP_LOSS:
            self.trade_state["stop_loss_hit"] = True
            print(f"{Fore.RED}[STOP LOSS DIÁRIO] P&L atual: R${self.trade_state['daily_pnl']:.2f}. Trading pausado.{Style.RESET_ALL}", flush=True)
        
        # Registrar no histórico
        self.trade_state["trade_history"].append({
            "pnl": pnl,
            "daily_pnl_total": self.trade_state["daily_pnl"]
        })
    
    def square_off_all_positions(self) -> Dict[str, Any]:
        """
        Fechar todas as posições ativas (square-off).
        
        Returns:
            Dicionário com resultado do square-off.
        """
        try:
            print(f"{Fore.YELLOW}[SQUARE-OFF] Fechando todas as posições ativas...{Style.RESET_ALL}", flush=True)
            
            closed_positions = []
            for symbol, position in list(self.trade_state["active_positions"].items()):
                quantity = position.get("quantity", 0)
                if quantity > 0:
                    # Enviar ordem de venda
                    result = self.place_order(symbol, "SELL", quantity)
                    if result.get("success"):
                        closed_positions.append(symbol)
            
            # Marcar que já fez square-off hoje
            self.trade_state["squared_off_today"] = True
            
            print(f"{Fore.GREEN}[SQUARE-OFF] ✓ {len(closed_positions)} posições fechadas{Style.RESET_ALL}", flush=True)
            
            return {"success": True, "closed_positions": closed_positions}
            
        except Exception as e:
            print(f"{Fore.RED}[ERRO NO SQUARE-OFF] {str(e)}{Style.RESET_ALL}", flush=True)
            return {"success": False, "error": str(e)}
    
    def reset_daily_state(self):
        """Resetar o estado diário para um novo dia de trading."""
        self.trade_state["trade_counts"] = {symbol: 0 for symbol in SYMBOLS}
        self.trade_state["stop_loss_hit"] = False
        self.trade_state["squared_off_today"] = False
        self.trade_state["daily_pnl"] = 0.0
        print(f"{Fore.CYAN}[RESET DIÁRIO] Estado resetado para novo dia de trading{Style.RESET_ALL}", flush=True)
