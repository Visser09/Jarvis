"""
Trading Strategy Module for Jarvis
"""
import numpy as np
import pandas as pd
from datetime import datetime
import time
import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class TradingStrategy:
    """Trading strategy implementation and execution"""
    
    def __init__(self, api_connector):
        """Initialize the trading strategy"""
        logger.info("Initializing Trading Strategy...")
        
        self.api = api_connector
        self.strategy_name = "Simple Moving Average Crossover"
        self.strategy_params = {
            "fast_ma": 9,
            "slow_ma": 21,
            "timeframe": "1D",
            "symbols": ["EURUSD", "GBPUSD", "USDJPY"]
        }
        
        # Load strategy parameters from file if available
        self._load_strategy_params()
        
        logger.info(f"Trading Strategy initialized: {self.strategy_name}")
    
    def _load_strategy_params(self):
        """Load strategy parameters from file"""
        try:
            if os.path.exists("data/trading/strategy_params.json"):
                with open("data/trading/strategy_params.json", "r") as f:
                    params = json.load(f)
                
                self.strategy_name = params.get("name", self.strategy_name)
                self.strategy_params.update(params.get("params", {}))
                
                logger.info(f"Loaded strategy parameters: {self.strategy_name}")
        except Exception as e:
            logger.error(f"Error loading strategy parameters: {str(e)}")
    
    def _save_strategy_params(self):
        """Save strategy parameters to file"""
        try:
            os.makedirs("data/trading", exist_ok=True)
            
            with open("data/trading/strategy_params.json", "w") as f:
                json.dump({
                    "name": self.strategy_name,
                    "params": self.strategy_params
                }, f, indent=2)
                
            logger.info("Strategy parameters saved to file.")
        except Exception as e:
            logger.error(f"Error saving strategy parameters: {str(e)}")
    
    def update_params(self, params):
        """Update strategy parameters"""
        self.strategy_params.update(params)
        self._save_strategy_params()
        logger.info(f"Strategy parameters updated: {params}")
    
    def analyze_market(self, symbol, timeframe=None):
        """Analyze market data for a symbol"""
        timeframe = timeframe or self.strategy_params["timeframe"]
        
        try:
            logger.info(f"Analyzing market data for {symbol} on {timeframe}")
            
            # Get market data
            market_data = self.api.get_market_data(symbol, timeframe, bars=100)
            
            if not market_data:
                logger.warning(f"No market data available for {symbol}")
                return {
                    "symbol": symbol,
                    "signal": "neutral",
                    "analysis": "No data available."
                }
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(market_data)
            
            # Calculate indicators
            fast_ma = self.strategy_params["fast_ma"]
            slow_ma = self.strategy_params["slow_ma"]
            
            df['fast_ma'] = df['close'].rolling(window=fast_ma).mean()
            df['slow_ma'] = df['close'].rolling(window=slow_ma).mean()
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1  # Buy signal
            df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1  # Sell signal
            
            # Get latest signal
            latest_signal = df['signal'].iloc[-1]
            signal_str = "buy" if latest_signal == 1 else "sell" if latest_signal == -1 else "neutral"
            
            # Calculate additional metrics
            current_price = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            price_change = (current_price - prev_close) / prev_close * 100
            
            # Calculate RSI (basic implementation)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Trend analysis
            trend = "uptrend" if df['close'].iloc[-1] > df['close'].iloc[-20:].mean() else "downtrend"
            
            # Compile analysis results
            analysis = {
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": round(current_price, 5),
                "price_change": round(price_change, 2),
                "signal": signal_str,
                "trend": trend,
                "indicators": {
                    f"MA{fast_ma}": round(df['fast_ma'].iloc[-1], 5),
                    f"MA{slow_ma}": round(df['slow_ma'].iloc[-1], 5),
                    "RSI": round(current_rsi, 1)
                },
                "analysis": f"The {fast_ma}/{slow_ma} MA crossover strategy gives a {signal_str} signal. "
                           f"The market is in an {trend} with RSI at {round(current_rsi, 1)}."
            }
            
            logger.info(f"Analysis complete for {symbol}: {signal_str} signal in {trend}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "signal": "error",
                "analysis": f"Error analyzing market: {str(e)}"
            }
    
    def analyze_all_markets(self):
        """Analyze all configured symbols"""
        results = []
        
        for symbol in self.strategy_params["symbols"]:
            result = self.analyze_market(symbol)
            results.append(result)
        
        return results
    
    def execute_trade(self, symbol, action, quantity):
        """Execute a trade based on analysis"""
        try:
            logger.info(f"Executing {action} trade for {quantity} {symbol}")
            
            # Validate action
            if action not in ["buy", "sell"]:
                logger.error(f"Invalid trade action: {action}")
                return {
                    "status": "error",
                    "message": f"Invalid trade action: {action}"
                }
            
            # Place order
            order = self.api.place_order(
                symbol=symbol,
                order_type=action,
                quantity=quantity
            )
            
            if order:
                return {
                    "status": "success",
                    "order_id": order["id"],
                    "message": f"{action.capitalize()} order for {quantity} {symbol} executed successfully."
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to execute trade."
                }
                
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing trade: {str(e)}"
            }
    
    def backtest_strategy(self, symbol, days=30):
        """Backtest the current strategy"""
        try:
            logger.info(f"Backtesting {self.strategy_name} on {symbol} for {days} days")
            
            # Get historical data
            market_data = self.api.get_market_data(symbol, self.strategy_params["timeframe"], bars=days)
            
            if not market_data:
                return {
                    "symbol": symbol,
                    "success": False,
                    "message": "No historical data available."
                }
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(market_data)
            
            # Calculate indicators
            fast_ma = self.strategy_params["fast_ma"]
            slow_ma = self.strategy_params["slow_ma"]
            
            df['fast_ma'] = df['close'].rolling(window=fast_ma).mean()
            df['slow_ma'] = df['close'].rolling(window=slow_ma).mean()
            
            # Generate signals
            df['signal'] = 0
            df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1  # Buy signal
            df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1  # Sell signal
            
            # Calculate returns
            df['position'] = df['signal'].shift(1)
            df['returns'] = df['close'].pct_change() * df['position']
            
            # Calculate performance metrics
            total_return = df['returns'].sum() * 100
            annualized_return = ((1 + df['returns'].sum()) ** (252 / len(df)) - 1) * 100
            sharpe_ratio = df['returns'].mean() / df['returns'].std() * np.sqrt(252)
            drawdown = (df['close'] / df['close'].cummax() - 1).min() * 100
            win_rate = len(df[df['returns'] > 0]) / len(df[df['returns'] != 0])
            
            # Count trades
            df['trade'] = df['signal'].diff().fillna(0)
            num_trades = len(df[df['trade'] != 0])
            
            # Compile results
            results = {
                "symbol": symbol,
                "strategy": self.strategy_name,
                "params": self.strategy_params,
                "period": f"{days} days",
                "total_return": round(total_return, 2),
                "annualized_return": round(annualized_return, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(drawdown, 2),
                "win_rate": round(win_rate * 100, 1),
                "num_trades": num_trades,
                "summary": f"The {fast_ma}/{slow_ma} MA crossover strategy generated "
                          f"{round(total_return, 2)}% return with a {round(win_rate * 100, 1)}% win rate "
                          f"over {days} days, with a max drawdown of {round(drawdown, 2)}%."
            }
            
            logger.info(f"Backtest completed for {symbol}: {round(total_return, 2)}% return")
            return results
            
        except Exception as e:
            logger.error(f"Error backtesting strategy: {str(e)}")
            return {
                "symbol": symbol,
                "success": False,
                "message": f"Error backtesting strategy: {str(e)}"
            }