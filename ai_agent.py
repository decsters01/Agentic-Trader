"""
Módulo do Agente de IA para o Agente de Trading.
Responsável por analisar dados de mercado, aprender com trades passados e tomar decisões.
"""
from typing import Dict, Any, List
import json
from colorama import Fore, Style

# Importar configurações
from config import TEMPERATURE, SENTIMENT_THRESHOLD_BUY, SENTIMENT_THRESHOLD_SELL, MODEL_PROVIDER


class AIAgent:
    """Agente de IA para análise de mercado e tomada de decisão de trading."""
    
    def __init__(self, client):
        """
        Inicializa o agente de IA.
        
        Args:
            client: Instância do cliente de modelo de IA (ex: LitellmModel).
        """
        self.client = client
    
    def analyze_market_sentiment(self, market_data_summary: str) -> tuple:
        """
        Envia dados de mercado para a IA e recebe análise de sentimento e tendência.
        
        Args:
            market_data_summary: String resumida com dados de mercado relevantes.
            
        Returns:
            Tupla contendo (score_de_sentimento, recomendacao_acao).
        """
        prompt = f"""
        Você é um assistente de trading especializado em mercado de ações indiano (NSE).
        Analise os dados de mercado resumidos abaixo e determine:
        1. Um score de sentimento (de 0 a 1, onde 0 é extremamente negativo e 1 é extremamente positivo).
        2. Uma recomendação clara de ação: "BUY", "SELL", ou "HOLD".

        Dados de Mercado Resumidos:
        {market_data_summary}

        Por favor, responda APENAS com um objeto JSON no formato:
        {{
          "sentiment_score": <float>,
          "recommendation": "<BUY/SELL/HOLD>"
        }}
        """

        try:
            # Obter nome do modelo baseado no provider
            model_map = {
                "cerebras": os.getenv("CEREBRAS_MODEL", "cerebras/gpt-oss-120b"),
                "groq": os.getenv("GROQ_MODEL", "groq/qwen/qwen3-32b"),
                "custom": os.getenv("CUSTOM_MODEL", "openai/gpt-4o-mini"),
                "openai": os.getenv("OPENAI_MODEL", "openai/gpt-5-mini")
            }
            model_name = model_map.get(MODEL_PROVIDER, model_map["openai"])
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            sentiment_score = float(analysis.get("sentiment_score", 0.5))
            recommendation = analysis.get("recommendation", "HOLD")
            
            print(f"{Fore.CYAN}[IA] Análise: Sentimento={sentiment_score:.2f}, Recomendação={recommendation}{Style.RESET_ALL}", flush=True)
            
            return sentiment_score, recommendation
            
        except Exception as e:
            print(f"{Fore.RED}[ERRO NA IA] Falha na análise: {e}{Style.RESET_ALL}", flush=True)
            return 0.5, "HOLD"  # Padrão neutro em caso de erro
    
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
