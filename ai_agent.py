"""
Módulo do Agente de IA para o Agente de Trading.
Responsável por analisar dados de mercado, aprender com trades passados e tomar decisões.
"""
from typing import Dict, Any, List
from colorama import Fore, Style

from config import SENTIMENT_THRESHOLD_BUY, SENTIMENT_THRESHOLD_SELL


class AIAgent:
    """Agente rule-based: sinais por indicadores e aprendizado com histórico; sem modelo de linguagem."""

    def __init__(self):
        pass

    def analyze_market_sentiment(self, symbol_data: dict) -> tuple:
        from indicator_signals import signal_from_indicators
        score, recommendation = signal_from_indicators(symbol_data)
        print(f"{Fore.CYAN}[SINAL] score={score:.2f}, recomendação={recommendation}{Style.RESET_ALL}", flush=True)
        return score, recommendation

    def analyze_past_trades(self, symbol: str, trade_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisar performance histórica de trades para um símbolo.

        Args:
            symbol: Símbolo do ativo para analisar.
            trade_history: Lista de trades passados para o símbolo.

        Returns:
            Dicionário com análise de performance, win rate e confiança.
        """
        symbol_trades = [t for t in trade_history if t.get("symbol") == symbol]

        if len(symbol_trades) < 3:
            return {
                "symbol": symbol,
                "confidence": "low",
                "reason": "Histórico de trades insuficiente (<3 trades)",
                "win_rate": 0,
                "avg_profit": 0
            }

        wins = [t for t in symbol_trades if t.get("pnl", 0) > 0]
        win_rate = len(wins) / len(symbol_trades) if symbol_trades else 0
        avg_profit = sum([t.get("pnl", 0) for t in symbol_trades]) / len(symbol_trades)

        # Encontrar padrões recentes
        recent_3 = symbol_trades[-3:]
        recent_success = sum([1 for t in recent_3 if t.get("pnl", 0) > 0])

        confidence = "high" if win_rate > 0.6 else "medium" if win_rate > 0.4 else "low"

        return {
            "symbol": symbol,
            "total_trades": len(symbol_trades),
            "win_rate": round(win_rate, 2),
            "avg_profit": round(avg_profit, 2),
            "recent_success": recent_success,
            "confidence": confidence,
            "reason": f"Win rate {win_rate:.0%}, lucro médio ₹{avg_profit:.2f}, últimos 3 trades: {recent_success}/3 vitórias"
        }

    @staticmethod
    def generate_learning_insights_static(trade_state: Dict[str, Any]) -> str:
        """
        Gerar insights de aprendizado baseados no estado atual dos trades (método estático).
        Evita criação desnecessária de instâncias da classe.

        Args:
            trade_state: Estado atual do gerenciamento de trades.

        Returns:
            String com insights e lições aprendidas.
        """
        insights = []

        # Analisar P&L diário
        daily_pnl = trade_state.get("daily_pnl", 0)
        if daily_pnl > 0:
            insights.append(f"Dia positivo com lucro de ₹{daily_pnl:.2f}.")
        elif daily_pnl < 0:
            insights.append(f"Dia negativo com prejuízo de ₹{abs(daily_pnl):.2f}.")
        else:
            insights.append("Dia neutro até o momento.")

        # Analisar símbolos mais performáticos
        if trade_state.get("trade_history"):
            symbol_performance = {}
            for trade in trade_state["trade_history"]:
                sym = trade.get("symbol")
                pnl = trade.get("pnl", 0)
                if sym not in symbol_performance:
                    symbol_performance[sym] = []
                symbol_performance[sym].append(pnl)

            best_symbol = max(symbol_performance.keys(),
                            key=lambda s: sum(symbol_performance[s])) if symbol_performance else None

            if best_symbol:
                total_pnl = sum(symbol_performance[best_symbol])
                insights.append(f"Melhor símbolo: {best_symbol} com lucro total de ₹{total_pnl:.2f}.")

        # Verificar se stop loss foi atingido
        if trade_state.get("stop_loss_hit"):
            insights.append("Stop loss diário atingido. Importante revisar estratégia.")

        return " ".join(insights) if insights else "Sem insights suficientes ainda."

    def generate_learning_insights(self, trade_state: Dict[str, Any]) -> str:
        """
        Gerar insights de aprendizado baseados no estado atual dos trades.
        Wrapper para o método estático.

        Args:
            trade_state: Estado atual do gerenciamento de trades.

        Returns:
            String com insights e lições aprendidas.
        """
        return self.generate_learning_insights_static(trade_state)

    def decide_action(self, sentiment_score: float, recommendation: str,
                     risk_analysis: Dict[str, Any], past_performance: Dict[str, Any]) -> str:
        """
        Tomar decisão final de ação baseada em múltiplos fatores.

        Args:
            sentiment_score: Score de sentimento da IA (0-1).
            recommendation: Recomendação inicial da IA ("BUY", "SELL", "HOLD").
            risk_analysis: Resultado da análise de restrições de risco.
            past_performance: Análise de performance passada para o símbolo.

        Returns:
            Decisão final de ação ("BUY", "SELL", "HOLD").
        """
        # Se análise de risco não permitir, retornar HOLD
        if not risk_analysis.get("allowed", False):
            print(f"{Fore.YELLOW}[DECISÃO] Trade bloqueado por risco: {risk_analysis.get('reason')}{Style.RESET_ALL}", flush=True)
            return "HOLD"

        # Ajustar decisão baseada em performance passada
        confidence = past_performance.get("confidence", "low")

        if recommendation == "BUY":
            if sentiment_score >= SENTIMENT_THRESHOLD_BUY:
                if confidence in ["high", "medium"]:
                    print(f"{Fore.GREEN}[DECISÃO] BUY confirmado (sentimento={sentiment_score:.2f}, confiança={confidence}){Style.RESET_ALL}", flush=True)
                    return "BUY"
                else:
                    print(f"{Fore.YELLOW}[DECISÃO] BUY cauteloso (confiança baixa){Style.RESET_ALL}", flush=True)
                    return "HOLD"
            else:
                print(f"{Fore.YELLOW}[DECISÃO] HOLD (sentimento abaixo do limiar){Style.RESET_ALL}", flush=True)
                return "HOLD"

        elif recommendation == "SELL":
            if sentiment_score <= SENTIMENT_THRESHOLD_SELL:
                print(f"{Fore.GREEN}[DECISÃO] SELL confirmado (sentimento={sentiment_score:.2f}, confiança={confidence}){Style.RESET_ALL}", flush=True)
                return "SELL"
            else:
                print(f"{Fore.YELLOW}[DECISÃO] HOLD (sentimento acima do limiar de venda){Style.RESET_ALL}", flush=True)
                return "HOLD"

        else:
            print(f"{Fore.CYAN}[DECISÃO] HOLD (recomendação neutra da IA){Style.RESET_ALL}", flush=True)
            return "HOLD"
