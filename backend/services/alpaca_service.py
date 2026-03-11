from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AlpacaService:
    """Service for Alpaca paper trading integration"""
    
    _trading_client = None
    _is_paper = True
    
    @classmethod
    def initialize(cls, api_key: str = None, secret_key: str = None, paper: bool = True):
        """Initialize Alpaca trading client"""
        try:
            # For now, we'll use mock mode if keys not provided
            cls._is_paper = paper
            
            if api_key and secret_key:
                cls._trading_client = TradingClient(
                    api_key=api_key,
                    secret_key=secret_key,
                    paper=paper
                )
                logger.info("Alpaca trading client initialized")
            else:
                logger.info("Alpaca running in MOCK mode (no API keys provided)")
                cls._trading_client = None
        
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca client: {e}")
            cls._trading_client = None
    
    @classmethod
    def get_account_info(cls) -> Dict:
        """Get account information"""
        try:
            if cls._trading_client:
                account = cls._trading_client.get_account()
                return {
                    "account_number": account.account_number,
                    "status": str(account.status),
                    "buying_power": float(account.buying_power),
                    "cash": float(account.cash),
                    "portfolio_value": float(account.portfolio_value),
                    "equity": float(account.equity),
                    "last_equity": float(account.last_equity),
                    "daily_pnl": float(account.equity) - float(account.last_equity),
                    "daily_pnl_percent": ((float(account.equity) - float(account.last_equity)) / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0,
                    "mode": "paper" if cls._is_paper else "live"
                }
            else:
                # Return mock data
                return {
                    "account_number": "MOCK_ACCOUNT",
                    "status": "ACTIVE",
                    "buying_power": 100000.0,
                    "cash": 100000.0,
                    "portfolio_value": 100000.0,
                    "equity": 100000.0,
                    "last_equity": 100000.0,
                    "daily_pnl": 0.0,
                    "daily_pnl_percent": 0.0,
                    "mode": "mock"
                }
        
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            # Return mock data on error
            return {
                "account_number": "MOCK_ACCOUNT",
                "status": "ACTIVE",
                "buying_power": 100000.0,
                "cash": 100000.0,
                "portfolio_value": 100000.0,
                "equity": 100000.0,
                "last_equity": 100000.0,
                "daily_pnl": 0.0,
                "daily_pnl_percent": 0.0,
                "mode": "mock"
            }
    
    @classmethod
    def submit_market_order(cls, symbol: str, qty: float, side: str) -> Dict:
        """Submit a market order"""
        try:
            if cls._trading_client:
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                
                order = cls._trading_client.submit_order(order_data=order_data)
                
                return {
                    "order_id": order.id,
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "side": str(order.side),
                    "status": str(order.status),
                    "submitted_at": str(order.submitted_at)
                }
            else:
                # Return mock order
                import uuid
                return {
                    "order_id": str(uuid.uuid4()),
                    "symbol": symbol,
                    "qty": qty,
                    "side": side,
                    "status": "ACCEPTED",
                    "submitted_at": str(datetime.now(timezone.utc))
                }
        
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            raise
    
    @classmethod
    def get_positions(cls) -> List[Dict]:
        """Get all open positions"""
        try:
            if cls._trading_client:
                positions = cls._trading_client.get_all_positions()
                
                return [
                    {
                        "symbol": pos.symbol,
                        "qty": float(pos.qty),
                        "side": "BUY" if float(pos.qty) > 0 else "SELL",
                        "entry_price": float(pos.avg_entry_price),
                        "current_price": float(pos.current_price),
                        "market_value": float(pos.market_value),
                        "unrealized_pnl": float(pos.unrealized_pl),
                        "unrealized_pnl_percent": float(pos.unrealized_plpc) * 100
                    }
                    for pos in positions
                ]
            else:
                # Return empty list for mock
                return []
        
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    @classmethod
    def get_orders(cls, status: str = "all") -> List[Dict]:
        """Get orders with optional status filter"""
        try:
            if cls._trading_client:
                status_enum = QueryOrderStatus.ALL
                if status == "open":
                    status_enum = QueryOrderStatus.OPEN
                elif status == "closed":
                    status_enum = QueryOrderStatus.CLOSED
                
                request_params = GetOrdersRequest(status=status_enum, limit=100)
                orders = cls._trading_client.get_orders(filter=request_params)
                
                return [
                    {
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "qty": float(order.qty),
                        "side": str(order.side),
                        "status": str(order.status),
                        "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                        "submitted_at": str(order.submitted_at)
                    }
                    for order in orders
                ]
            else:
                # Return empty list for mock
                return []
        
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []


# Initialize on import with mock mode
AlpacaService.initialize()
