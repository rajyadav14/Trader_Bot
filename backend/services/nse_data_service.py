import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)


class NSEDataService:
    """Service for fetching NSE/BSE market data
    
    Note: This uses free NSE APIs for demonstration.
    For production, integrate with TrueData, Global Datafeeds, or m.Stock
    """
    
    BASE_URL = "https://www.nseindia.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # Popular NSE stocks with tokens (for demo)
    SYMBOL_TOKENS = {
        "RELIANCE": "2885",
        "TCS": "11536",
        "HDFCBANK": "1333",
        "INFY": "1594",
        "ICICIBANK": "4963",
        "SBIN": "3045",
        "BHARTIARTL": "10604",
        "HINDUNILVR": "1394",
        "ITC": "1660",
        "KOTAKBANK": "1922",
        "LT": "11483",
        "AXISBANK": "5900",
        "ASIANPAINT": "3718",
        "MARUTI": "10999",
        "TATAMOTORS": "3456",
        "NIFTY50": "99926000",
        "BANKNIFTY": "99926009"
    }
    
    @staticmethod
    def get_session():
        """Create NSE session with cookies"""
        session = requests.Session()
        session.headers.update(NSEDataService.HEADERS)
        
        try:
            # Get cookies
            session.get(NSEDataService.BASE_URL, timeout=10)
        except:
            pass
        
        return session
    
    @staticmethod
    def get_quote(symbol: str) -> Optional[Dict]:
        """Get current quote for NSE symbol"""
        try:
            session = NSEDataService.get_session()
            url = f"{NSEDataService.BASE_URL}/api/quote-equity?symbol={symbol}"
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price_info = data.get('priceInfo', {})
                
                return {
                    "symbol": symbol,
                    "token": NSEDataService.SYMBOL_TOKENS.get(symbol, "0"),
                    "ltp": float(price_info.get('lastPrice', 0)),
                    "open": float(price_info.get('open', 0)),
                    "high": float(price_info.get('intraDayHighLow', {}).get('max', 0)),
                    "low": float(price_info.get('intraDayHighLow', {}).get('min', 0)),
                    "close": float(price_info.get('close', 0)),
                    "volume": int(data.get('securityWiseDP', {}).get('quantityTraded', 0)),
                    "change": float(price_info.get('change', 0)),
                    "pchange": float(price_info.get('pChange', 0))
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_historical_data(symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for NSE symbol
        
        Note: For production, use TrueData or Global Datafeeds API
        This is a simplified version using available free data
        """
        try:
            # Generate mock historical data based on current price
            quote = NSEDataService.get_quote(symbol)
            
            if not quote:
                return pd.DataFrame()
            
            # Generate synthetic historical data (for demo)
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            current_price = quote['ltp']
            
            # Random walk simulation
            returns = np.random.normal(0.001, 0.02, days)
            prices = current_price * np.exp(np.cumsum(returns))
            
            df = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
                'high': prices * (1 + np.random.uniform(0, 0.02, days)),
                'low': prices * (1 - np.random.uniform(0, 0.02, days)),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, days)
            })
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_nifty_stocks() -> List[str]:
        """Get list of NIFTY 50 stocks"""
        return list(NSEDataService.SYMBOL_TOKENS.keys())
    
    @staticmethod
    def get_fii_dii_data() -> Dict:
        """Get FII/DII data (simplified)
        
        Note: For production, scrape NSE reports or use data provider
        """
        try:
            # Mock FII/DII data
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "fii_net_cash": np.random.uniform(-1000, 1000),  # Crores
                "fii_net_derivative": np.random.uniform(-500, 500),
                "dii_net_cash": np.random.uniform(-800, 800),
                "dii_net_derivative": np.random.uniform(-300, 300)
            }
        
        except Exception as e:
            logger.error(f"Error fetching FII/DII data: {e}")
            return {}
