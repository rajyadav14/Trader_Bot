from fastapi import APIRouter, HTTPException
from services.nse_data_service import NSEDataService
from services.technical_analysis_service import TechnicalAnalysisService
from services.sentiment_analysis_service import SentimentAnalysisService
from services.signal_fusion_service import SignalFusionService
from services.angel_one_service import AngelOneService
from models.ml_models import ensemble_model
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nse", tags=["nse-trading"])

# Initialize services
sentiment_service = SentimentAnalysisService()

# NSE Stock Watchlist
NSE_WATCHLIST = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "SBIN", "BHARTIARTL", "HINDUNILVR", "ITC", "KOTAKBANK",
    "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TATAMOTORS"
]


@router.get("/health")
async def nse_health_check():
    """NSE trading system health check"""
    return {
        "status": "healthy",
        "service": "ORACLE NSE/BSE Trading System",
        "angel_one_status": "connected" if AngelOneService._smart_api else "demo_mode",
        "ml_models": {
            "ensemble": "trained" if ensemble_model.is_trained else "ready",
            "xgboost": "available" if ensemble_model.models.get('xgboost') else "not_trained",
            "lightgbm": "available" if ensemble_model.models.get('lightgbm') else "not_trained",
            "random_forest": "available" if ensemble_model.models.get('random_forest') else "not_trained"
        }
    }


@router.get("/account")
async def get_nse_account():
    """Get Angel One account information"""
    try:
        account_info = AngelOneService.get_account_info()
        funds = AngelOneService.get_funds()
        
        return {
            **account_info,
            "funds": funds,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching NSE account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quote/{symbol}")
async def get_nse_quote(symbol: str):
    """Get real-time NSE quote"""
    try:
        quote = NSEDataService.get_quote(symbol.upper())
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
        
        return quote
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching NSE quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/technical-analysis/{symbol}")
async def get_nse_technical_analysis(symbol: str):
    """Get technical analysis for NSE symbol"""
    try:
        # Get historical data
        df = NSEDataService.get_historical_data(symbol.upper(), days=100)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Run technical analysis
        analysis = TechnicalAnalysisService.analyze_stock(df, symbol.upper())
        
        # Add ML signal
        ml_signal = ensemble_model.get_signal(df, analysis)
        analysis['ml_signal'] = ml_signal
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}")
async def get_nse_signals(symbol: str):
    """Get fused AI signals for NSE symbol (including ML)"""
    try:
        symbol = symbol.upper()
        
        # Get historical data
        df = NSEDataService.get_historical_data(symbol, days=100)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Get technical analysis
        technical_analysis = TechnicalAnalysisService.analyze_stock(df, symbol)
        technical_signal = technical_analysis.get('signal', {})
        technical_signal['layer'] = 'technical'
        
        # Get sentiment analysis  
        sentiment_result = sentiment_service.analyze_symbol_sentiment(symbol)
        
        # Get ML ensemble signal
        ml_signal = ensemble_model.get_signal(df, technical_analysis)
        
        # Fuse all signals (technical + sentiment + ML)
        signals_to_fuse = [technical_signal, sentiment_result, ml_signal]
        
        # Calculate weighted fusion
        buy_votes = sum(1 for s in signals_to_fuse if s.get('direction') == 'BUY')
        sell_votes = sum(1 for s in signals_to_fuse if s.get('direction') == 'SELL')
        hold_votes = sum(1 for s in signals_to_fuse if s.get('direction') == 'HOLD')
        
        total_votes = len(signals_to_fuse)
        consensus = (max(buy_votes, sell_votes, hold_votes) / total_votes) * 100
        
        # Determine direction
        if buy_votes > sell_votes and buy_votes > hold_votes:
            direction = "BUY"
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            direction = "SELL"
        else:
            direction = "HOLD"
        
        # Calculate weighted strength and confidence
        total_strength = sum(s.get('strength', 5) for s in signals_to_fuse)
        avg_strength = total_strength / total_votes
        
        total_confidence = sum(s.get('confidence', 50) for s in signals_to_fuse)
        avg_confidence = total_confidence / total_votes
        
        # Determine if should trade (higher threshold with ML)
        should_trade = (
            avg_confidence >= 70 and  # Slightly lower threshold
            avg_strength >= 6.5 and   # Slightly lower threshold  
            direction in ["BUY", "SELL"]
        )
        
        # Get current price
        quote = NSEDataService.get_quote(symbol)
        current_price = quote['ltp'] if quote else technical_analysis.get('current_price', 0)
        
        # Get account info for position sizing
        funds = AngelOneService.get_funds()
        
        # Calculate position size
        position_size = SignalFusionService.calculate_position_size(
            account_equity=funds.get('net_available', 100000),
            signal_strength=avg_strength,
            signal_confidence=avg_confidence,
            max_position_pct=5.0
        )
        
        # Calculate shares
        shares = int(position_size / current_price) if current_price > 0 else 0
        
        fused_signal = {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "strength": round(avg_strength, 1),
            "confidence": round(avg_confidence, 1),
            "consensus": round(consensus, 1),
            "should_trade": should_trade,
            "buy_votes": buy_votes,
            "sell_votes": sell_votes,
            "hold_votes": hold_votes,
            "total_signals": total_votes,
            "current_price": current_price,
            "recommended_position_size": position_size,
            "recommended_shares": shares,
            "layer_signals": signals_to_fuse,
            "exchange": "NSE",
            "token": quote.get('token') if quote else NSEDataService.SYMBOL_TOKENS.get(symbol, "0")
        }
        
        return fused_signal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def get_nse_watchlist():
    """Get NSE watchlist stocks"""
    return {
        "watchlist": NSE_WATCHLIST,
        "count": len(NSE_WATCHLIST),
        "exchange": "NSE"
    }


@router.get("/positions")
async def get_nse_positions():
    """Get all NSE positions"""
    try:
        positions = AngelOneService.get_positions()
        return {
            "positions": positions,
            "count": len(positions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fii-dii")
async def get_fii_dii_data():
    """Get FII/DII institutional flow data"""
    try:
        data = NSEDataService.get_fii_dii_data()
        return data
    except Exception as e:
        logger.error(f"Error fetching FII/DII data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_nse_performance():
    """Get NSE trading performance metrics"""
    try:
        funds = AngelOneService.get_funds()
        
        equity = funds.get('net_available', 100000)
        starting_equity = 100000.0
        
        total_pnl = equity - starting_equity
        total_pnl_percent = (total_pnl / starting_equity) * 100
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "equity": equity,
            "cash": funds.get('available_cash', 0),
            "portfolio_value": equity,
            "daily_pnl": 0,  # TODO: Calculate from trade history
            "daily_pnl_percent": 0,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "sharpe_ratio": None,
            "max_drawdown": None,
            "win_rate": None,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "exchange": "NSE"
        }
    
    except Exception as e:
        logger.error(f"Error calculating performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
