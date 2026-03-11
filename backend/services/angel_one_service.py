from SmartApi import SmartConnect
import pyotp
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)


class AngelOneService:
    """Service for Angel One SmartAPI integration for NSE/BSE trading"""
    
    _smart_api = None
    _jwt_token = None
    _refresh_token = None
    _feed_token = None
    _session_data = None
    
    # Demo credentials (user will replace with their own)
    DEMO_API_KEY = "demo_key"
    DEMO_USERNAME = "demo_user"
    DEMO_PASSWORD = "demo_pass"
    DEMO_TOTP_SECRET = "demo_secret"
    
    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_STOPLOSS = "STOPLOSS_LIMIT"
    
    # Product types
    PRODUCT_INTRADAY = "INTRADAY"
    PRODUCT_DELIVERY = "DELIVERY"
    PRODUCT_CARRYFORWARD = "CARRYFORWARD"  # F&O
    
    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"  # NSE F&O
    EXCHANGE_BFO = "BFO"  # BSE F&O
    
    @classmethod
    def initialize(cls, api_key: str = None, username: str = None, 
                   password: str = None, totp_secret: str = None):
        """Initialize Angel One SmartAPI client"""
        try:
            # Use provided credentials or demo
            api_key = api_key or cls.DEMO_API_KEY
            username = username or cls.DEMO_USERNAME
            password = password or cls.DEMO_PASSWORD
            totp_secret = totp_secret or cls.DEMO_TOTP_SECRET
            
            # Check if using demo credentials
            if api_key == cls.DEMO_API_KEY:
                logger.info("Angel One running in DEMO/MOCK mode (no API keys provided)")
                cls._smart_api = None
                return
            
            # Initialize SmartAPI
            cls._smart_api = SmartConnect(api_key=api_key)
            
            # Authenticate
            cls._authenticate(username, password, totp_secret)
            
            logger.info("Angel One SmartAPI initialized and authenticated")
        
        except Exception as e:
            logger.error(f"Failed to initialize Angel One client: {e}")
            cls._smart_api = None
    
    @classmethod
    def _generate_totp(cls, secret: str) -> str:
        """Generate TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    @classmethod
    def _authenticate(cls, username: str, password: str, totp_secret: str):
        """Authenticate with Angel One"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                totp_code = cls._generate_totp(totp_secret)
                
                session_data = cls._smart_api.generateSession(
                    username, password, totp_code
                )
                
                if not session_data.get('status'):
                    error_msg = session_data.get('message', 'Unknown error')
                    logger.warning(f"Authentication failed: {error_msg}")
                    
                    if 'totp' in error_msg.lower() and attempt < max_attempts - 1:
                        logger.info(f"TOTP expired, retrying (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(2)
                        continue
                    else:
                        raise Exception(f"Authentication failed: {error_msg}")
                
                cls._session_data = session_data['data']
                cls._jwt_token = cls._session_data.get('jwtToken')
                cls._refresh_token = cls._session_data.get('refreshToken')
                cls._feed_token = cls._smart_api.getfeedToken()
                
                logger.info("Authentication successful")
                return True
            
            except Exception as e:
                logger.error(f"Authentication attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
        
        raise Exception(f"Authentication failed after {max_attempts} attempts")
    
    @classmethod
    def get_account_info(cls) -> Dict:
        """Get account information"""
        try:
            if cls._smart_api and cls._refresh_token:
                profile = cls._smart_api.getProfile(cls._refresh_token)
                
                if profile.get('status'):
                    user_data = profile.get('data', {})
                    return {
                        "client_id": user_data.get('clientcode'),
                        "name": user_data.get('name'),
                        "email": user_data.get('email'),
                        "exchanges": user_data.get('exchanges', []),
                        "products": user_data.get('products', []),
                        "mode": "live"
                    }
                else:
                    raise Exception(f"Failed to fetch profile: {profile.get('message')}")
            else:
                # Return mock data
                return {
                    "client_id": "DEMO123",
                    "name": "Demo User",
                    "email": "demo@example.com",
                    "exchanges": ["NSE", "BSE", "NFO"],
                    "products": ["INTRADAY", "DELIVERY", "CARRYFORWARD"],
                    "mode": "demo"
                }
        
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {
                "client_id": "DEMO123",
                "name": "Demo User",
                "email": "demo@example.com",
                "exchanges": ["NSE", "BSE", "NFO"],
                "products": ["INTRADAY", "DELIVERY", "CARRYFORWARD"],
                "mode": "demo"
            }
    
    @classmethod
    def get_funds(cls) -> Dict:
        """Get available funds"""
        try:
            if cls._smart_api:
                funds = cls._smart_api.getRMS()
                
                if funds.get('status'):
                    fund_data = funds.get('data', {})
                    return {
                        "available_cash": float(fund_data.get('availablecash', 0)),
                        "used_margin": float(fund_data.get('m2munrealized', 0)),
                        "net_available": float(fund_data.get('net', 0))
                    }
            
            # Mock data
            return {
                "available_cash": 100000.0,
                "used_margin": 0.0,
                "net_available": 100000.0
            }
        
        except Exception as e:
            logger.error(f"Error getting funds: {e}")
            return {
                "available_cash": 100000.0,
                "used_margin": 0.0,
                "net_available": 100000.0
            }
    
    @classmethod
    def place_order(cls, symbol: str, token: str, exchange: str, 
                   quantity: int, order_type: str, transaction_type: str,
                   product_type: str = None, price: float = None) -> Dict:
        """Place a trading order"""
        try:
            if cls._smart_api:
                order_params = {
                    "variety": "NORMAL",
                    "tradingsymbol": symbol,
                    "symboltoken": token,
                    "transactiontype": transaction_type,
                    "exchange": exchange,
                    "ordertype": order_type,
                    "producttype": product_type or cls.PRODUCT_INTRADAY,
                    "duration": "DAY",
                    "quantity": str(quantity),
                    "squareoff": "0",
                    "stoploss": "0"
                }
                
                if price:
                    order_params["price"] = str(price)
                
                response = cls._smart_api.placeOrderFullResponse(order_params)
                
                if response.get('status'):
                    order_data = response.get('data', {})
                    return {
                        "order_id": order_data.get('orderid'),
                        "unique_order_id": order_data.get('uniqueorderid'),
                        "status": "success"
                    }
                else:
                    raise Exception(f"Order placement failed: {response.get('message')}")
            else:
                # Mock order
                import uuid
                return {
                    "order_id": str(uuid.uuid4())[:8],
                    "unique_order_id": str(uuid.uuid4()),
                    "status": "success (demo)"
                }
        
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    @classmethod
    def get_positions(cls) -> List[Dict]:
        """Get all open positions"""
        try:
            if cls._smart_api:
                response = cls._smart_api.getPosition()
                
                if response.get('status'):
                    positions = response.get('data', [])
                    return [
                        {
                            "symbol": pos.get('tradingsymbol'),
                            "exchange": pos.get('exchange'),
                            "quantity": int(pos.get('netqty', 0)),
                            "avg_price": float(pos.get('netprice', 0)),
                            "ltp": float(pos.get('ltp', 0)),
                            "pnl": float(pos.get('pnl', 0)),
                            "product_type": pos.get('producttype')
                        }
                        for pos in positions if int(pos.get('netqty', 0)) != 0
                    ]
            
            # Return empty list for demo
            return []
        
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []


# Initialize on import with demo mode
AngelOneService.initialize()
