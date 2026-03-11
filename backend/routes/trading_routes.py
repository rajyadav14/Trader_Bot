from fastapi import APIRouter, HTTPException
from services.market_data_service import MarketDataService
from services.technical_analysis_service import TechnicalAnalysisService
from services.sentiment_analysis_service import SentimentAnalysisService
from services.signal_fusion_service import SignalFusionService
from services.alpaca_service import AlpacaService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["oracle"])

# Initialize services
sentiment_service = SentimentAnalysisService()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ORACLE Trading System"}


@router.get("/account")
async def get_account():
    """Get account information"""
    try:
        account_info = AlpacaService.get_account_info()
        return account_info
    except Exception as e:
        logger.error(f"Error fetching account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str, period: str = "1mo"):
    """Get historical market data for a symbol"""
    try:
        df = MarketDataService.get_historical_data(symbol, period=period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Convert to list of dicts
        data = df.to_dict('records')
        
        # Convert timestamps to strings
        for record in data:
            if 'date' in record:
                record['date'] = str(record['date'])
            elif 'datetime' in record:
                record['datetime'] = str(record['datetime'])
        
        return {
            "symbol": symbol,
            "period": period,
            "data": data,
            "count": len(data)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/technical-analysis/{symbol}")
async def get_technical_analysis(symbol: str):
    """Get technical analysis for a symbol"""
    try:
        df = MarketDataService.get_historical_data(symbol, period="6mo")
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        analysis = TechnicalAnalysisService.analyze_stock(df, symbol)
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment-analysis/{symbol}")
async def get_sentiment_analysis(symbol: str):
    """Get AI sentiment analysis for a symbol"""
    try:
        result = sentiment_service.analyze_symbol_sentiment(symbol)
        return result
    
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}")
async def get_fused_signals(symbol: str):
    """Get fused AI signals for a symbol"""
    try:
        # Get technical analysis
        df = MarketDataService.get_historical_data(symbol, period="6mo")
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        technical_analysis = TechnicalAnalysisService.analyze_stock(df, symbol)
        technical_signal = technical_analysis.get('signal', {})
        technical_signal['layer'] = 'technical'
        
        # Get sentiment analysis
        sentiment_result = sentiment_service.analyze_symbol_sentiment(symbol)
        
        # Fuse signals
        fused_signal = SignalFusionService.fuse_signals(
            technical_signal,
            sentiment_result,
            symbol
        )
        
        # Get current price
        current_price = technical_analysis.get('current_price', 0)
        
        # Get account info for position sizing
        account = AlpacaService.get_account_info()
        
        # Calculate position size
        position_size = SignalFusionService.calculate_position_size(
            account_equity=account.get('equity', 100000),
            signal_strength=fused_signal.get('strength', 5),
            signal_confidence=fused_signal.get('confidence', 50)
        )
        
        # Calculate shares
        shares = int(position_size / current_price) if current_price > 0 else 0
        
        fused_signal['current_price'] = current_price
        fused_signal['recommended_position_size'] = position_size
        fused_signal['recommended_shares'] = shares
        
        return fused_signal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions():
    """Get all current positions"""
    try:
        positions = AlpacaService.get_positions()
        return {"positions": positions, "count": len(positions)}
    
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(status: str = "all"):
    """Get orders"""
    try:
        orders = AlpacaService.get_orders(status=status)
        return {"orders": orders, "count": len(orders)}
    
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes")
async def get_quotes(symbols: str):
    """Get current quotes for multiple symbols"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        quotes = MarketDataService.get_multiple_quotes(symbol_list)
        
        return {
            "quotes": quotes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance():
    """Get performance metrics"""
    try:
        account = AlpacaService.get_account_info()
        
        # Calculate metrics
        equity = account.get('equity', 100000)
        starting_equity = 100000.0
        
        total_pnl = equity - starting_equity
        total_pnl_percent = (total_pnl / starting_equity) * 100
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "equity": equity,
            "cash": account.get('cash', 0),
            "portfolio_value": account.get('portfolio_value', 0),
            "daily_pnl": account.get('daily_pnl', 0),
            "daily_pnl_percent": account.get('daily_pnl_percent', 0),
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "sharpe_ratio": None,  # TODO: Calculate from historical data
            "max_drawdown": None,  # TODO: Calculate from historical data
            "win_rate": None  # TODO: Calculate from trade history
        }
    
    except Exception as e:
        logger.error(f"Error calculating performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime, timezone
