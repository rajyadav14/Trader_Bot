import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data using yfinance"""
    
    @staticmethod
    def get_historical_data(
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Fetch historical market data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_current_price(symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                return None
            
            return float(data['Close'].iloc[-1])
        
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_multiple_quotes(symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        quotes = {}
        
        for symbol in symbols:
            price = MarketDataService.get_current_price(symbol)
            if price:
                quotes[symbol] = price
        
        return quotes
    
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = "5m") -> pd.DataFrame:
        """Get intraday data for real-time analysis"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval=interval)
            
            if df.empty:
                return pd.DataFrame()
            
            df.reset_index(inplace=True)
            df.columns = [col.lower() for col in df.columns]
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_market_info(symbol: str) -> Dict:
        """Get comprehensive market info"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", 1.0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0)
            }
        
        except Exception as e:
            logger.error(f"Error fetching market info for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
