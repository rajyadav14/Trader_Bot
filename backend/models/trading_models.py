from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class MarketRegime(str, Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"
    NEWS_DRIVEN = "NEWS_DRIVEN"


class MarketData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = "1d"


class TechnicalIndicators(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    symbol: str
    timestamp: datetime
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    obv: Optional[float] = None


class AISignal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    symbol: str
    timestamp: datetime
    layer: str  # technical, sentiment, quantitative, macro, prediction
    signal_direction: str  # BUY, SELL, HOLD
    signal_strength: float  # 1-10
    confidence: float  # 0-100
    reasoning: str
    metadata: Optional[Dict] = None


class FusedSignal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    symbol: str
    timestamp: datetime
    direction: str  # BUY, SELL, HOLD
    strength: float  # 1-10
    confidence: float  # 0-100
    consensus: float  # % of layers agreeing
    layer_signals: List[AISignal]
    should_trade: bool


class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    trade_id: str
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: OrderStatus
    entry_time: datetime
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    entry_reason: str
    exit_reason: Optional[str] = None
    ai_confidence: float
    fused_signal: Optional[Dict] = None


class Position(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    ai_confidence: float
    entry_time: datetime
    last_updated: datetime


class PerformanceMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    timestamp: datetime
    equity: float
    cash: float
    portfolio_value: float
    daily_pnl: float
    daily_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0


class AccountInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    account_number: str
    status: str
    buying_power: float
    cash: float
    portfolio_value: float
    equity: float
    last_equity: float
    daily_pnl: float
    daily_pnl_percent: float


class RiskMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    timestamp: datetime
    total_exposure: float
    portfolio_var: float
    max_position_size: float
    sector_exposure: Dict[str, float]
    daily_loss_limit: float
    daily_loss_remaining: float
    is_trading_paused: bool
