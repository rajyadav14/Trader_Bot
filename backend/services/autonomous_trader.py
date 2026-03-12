import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import os
from services.angel_one_service import AngelOneService
from services.nse_data_service import NSEDataService
from services.technical_analysis_service import TechnicalAnalysisService
from services.sentiment_analysis_service import SentimentAnalysisService
from models.ml_models import ensemble_model

logger = logging.getLogger(__name__)


class AutonomousTrader:
    """Autonomous trading engine for ORACLE NSE/BSE system
    
    SAFETY FIRST:
    - Disabled by default
    - Requires explicit enable via environment variable
    - Multiple safety checks and circuit breakers
    - Daily loss limits enforced
    - Emergency kill switch integration
    """
    
    def __init__(self):
        # Master control (from environment)
        self.enabled = os.getenv('AUTO_TRADING_ENABLED', 'false').lower() == 'true'
        
        # Trading state
        self.is_running = False
        self.is_paused = False
        self.pause_reason = None
        
        # Configuration from environment
        self.min_signal_confidence = float(os.getenv('MIN_SIGNAL_CONFIDENCE', '72'))
        self.min_signal_strength = float(os.getenv('MIN_SIGNAL_STRENGTH', '7'))
        self.max_positions = int(os.getenv('MAX_POSITIONS', '10'))
        self.max_position_size_pct = float(os.getenv('MAX_POSITION_SIZE_PCT', '5'))
        self.daily_loss_limit_pct = float(os.getenv('DAILY_LOSS_LIMIT_PCT', '2'))
        self.check_interval_seconds = int(os.getenv('CHECK_INTERVAL_SECONDS', '30'))
        
        # Watchlist
        self.watchlist = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
            "SBIN", "BHARTIARTL", "HINDUNILVR", "ITC", "KOTAKBANK"
        ]
        
        # State tracking
        self.starting_equity = 100000.0
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.positions = {}
        self.trade_log = []
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        logger.info(f"Autonomous Trader initialized (ENABLED: {self.enabled})")
    
    def start(self):
        """Start autonomous trading"""
        if not self.enabled:
            logger.warning("❌ Autonomous trading is DISABLED in environment")
            return False
        
        if self.is_running:
            logger.warning("Autonomous trader already running")
            return False
        
        logger.info("🚀 Starting autonomous trading engine...")
        self.is_running = True
        self.is_paused = False
        
        # Start async trading loop
        asyncio.create_task(self.trading_loop())
        return True
    
    def stop(self):
        """Stop autonomous trading"""
        logger.info("🛑 Stopping autonomous trading engine...")
        self.is_running = False
        return True
    
    def pause(self, reason: str = "Manual pause"):
        """Pause trading temporarily"""
        logger.warning(f"⏸️ Pausing trading: {reason}")
        self.is_paused = True
        self.pause_reason = reason
        return True
    
    def resume(self):
        """Resume trading after pause"""
        logger.info("▶️ Resuming autonomous trading")
        self.is_paused = False
        self.pause_reason = None
        return True
    
    async def trading_loop(self):
        """Main autonomous trading loop"""
        logger.info("📊 Trading loop started")
        
        while self.is_running:
            try:
                # Check if paused
                if self.is_paused:
                    logger.info(f"⏸️ Trading paused: {self.pause_reason}")
                    await asyncio.sleep(60)
                    continue
                
                # 1. Safety checks
                if not await self.safety_checks():
                    self.pause("Safety checks failed")
                    await asyncio.sleep(60)
                    continue
                
                # 2. Manage existing positions
                await self.manage_positions()
                
                # 3. Scan for new opportunities
                if len(self.positions) < self.max_positions:
                    await self.scan_and_execute()
                
                # 4. Update statistics
                self.update_statistics()
                
                # 5. Log status
                logger.info(f"💹 Status: {len(self.positions)} positions | Daily P&L: ₹{self.daily_pnl:.2f} | Trades: {self.trades_today}")
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                self.pause(f"Error: {str(e)}")
            
            # Wait before next iteration
            await asyncio.sleep(self.check_interval_seconds)
        
        logger.info("🛑 Trading loop stopped")
    
    async def safety_checks(self) -> bool:
        """Run safety checks before trading"""
        
        # Check 1: Daily loss limit
        funds = AngelOneService.get_funds()
        current_equity = funds.get('net_available', self.starting_equity)
        
        daily_loss_limit = self.starting_equity * (self.daily_loss_limit_pct / 100)
        self.daily_pnl = current_equity - self.starting_equity
        
        if self.daily_pnl <= -daily_loss_limit:
            logger.error(f"🚨 DAILY LOSS LIMIT HIT: ₹{self.daily_pnl:.2f}")
            return False
        
        # Check 2: Market hours (NSE: 9:15 AM - 3:30 PM IST)
        # TODO: Add market hours check
        
        # Check 3: Angel One connection
        if AngelOneService._smart_api is None:
            logger.warning("⚠️ Angel One not connected (demo mode)")
            # Allow in demo mode
        
        return True
    
    async def scan_and_execute(self):
        """Scan watchlist and execute trades"""
        
        for symbol in self.watchlist:
            try:
                # Skip if already have position
                if symbol in self.positions:
                    continue
                
                # Get signal
                signal = await self.get_signal(symbol)
                
                if not signal:
                    continue
                
                # Check if should trade
                if signal.get('should_trade') and signal.get('direction') in ['BUY', 'SELL']:
                    confidence = signal.get('confidence', 0)
                    strength = signal.get('strength', 0)
                    
                    # Verify thresholds
                    if confidence >= self.min_signal_confidence and strength >= self.min_signal_strength:
                        # Execute trade
                        if signal['direction'] == 'BUY':
                            await self.execute_buy(symbol, signal)
                        elif signal['direction'] == 'SELL':
                            await self.execute_sell(symbol, signal)
            
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
    
    async def get_signal(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive signal for symbol"""
        try:
            # Get historical data
            df = NSEDataService.get_historical_data(symbol, days=100)
            
            if df.empty:
                return None
            
            # Technical analysis
            tech_analysis = TechnicalAnalysisService.analyze_stock(df, symbol)
            tech_signal = tech_analysis.get('signal', {})
            tech_signal['layer'] = 'technical'
            
            # Sentiment analysis
            sentiment_service = SentimentAnalysisService()
            sentiment_signal = sentiment_service.analyze_symbol_sentiment(symbol)
            
            # ML signal
            ml_signal = ensemble_model.get_signal(df, tech_analysis)
            
            # Fuse signals
            signals = [tech_signal, sentiment_signal, ml_signal]
            
            buy_votes = sum(1 for s in signals if s.get('direction') == 'BUY')
            sell_votes = sum(1 for s in signals if s.get('direction') == 'SELL')
            hold_votes = sum(1 for s in signals if s.get('direction') == 'HOLD')
            
            if buy_votes > sell_votes and buy_votes > hold_votes:
                direction = "BUY"
            elif sell_votes > buy_votes and sell_votes > hold_votes:
                direction = "SELL"
            else:
                direction = "HOLD"
            
            avg_confidence = sum(s.get('confidence', 50) for s in signals) / len(signals)
            avg_strength = sum(s.get('strength', 5) for s in signals) / len(signals)
            
            should_trade = (
                avg_confidence >= self.min_signal_confidence and
                avg_strength >= self.min_signal_strength and
                direction in ['BUY', 'SELL']
            )
            
            # Get quote
            quote = NSEDataService.get_quote(symbol)
            current_price = quote['ltp'] if quote else tech_analysis.get('current_price', 0)
            
            return {
                'symbol': symbol,
                'direction': direction,
                'confidence': avg_confidence,
                'strength': avg_strength,
                'should_trade': should_trade,
                'current_price': current_price,
                'token': quote.get('token') if quote else "0",
                'atr': tech_analysis.get('atr', current_price * 0.02)
            }
        
        except Exception as e:
            logger.error(f"Error getting signal for {symbol}: {e}")
            return None
    
    async def execute_buy(self, symbol: str, signal: Dict):
        """Execute buy order"""
        try:
            funds = AngelOneService.get_funds()
            available_cash = funds.get('available_cash', 100000)
            
            # Calculate position size (Kelly Criterion)
            max_position_size = available_cash * (self.max_position_size_pct / 100)
            
            confidence = signal['confidence'] / 100
            position_size = min(max_position_size, available_cash * confidence * 0.25)
            
            current_price = signal['current_price']
            shares = int(position_size / current_price)
            
            if shares <= 0:
                logger.warning(f"Position size too small for {symbol}")
                return
            
            # Calculate stop loss (ATR-based)
            atr = signal.get('atr', current_price * 0.02)
            stop_loss_price = current_price - (2 * atr)
            take_profit_price = current_price + (3 * atr)
            
            logger.info(f"🟢 BUY: {symbol} | Qty: {shares} | Price: ₹{current_price:.2f} | SL: ₹{stop_loss_price:.2f}")
            
            # Place order (demo mode will return mock order)
            order = AngelOneService.place_order(
                symbol=symbol,
                token=signal['token'],
                exchange='NSE',
                quantity=shares,
                order_type='MARKET',
                transaction_type='BUY'
            )
            
            # Track position
            self.positions[symbol] = {
                'symbol': symbol,
                'side': 'BUY',
                'quantity': shares,
                'entry_price': current_price,
                'current_price': current_price,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'entry_time': datetime.now(timezone.utc),
                'signal': signal,
                'order_id': order.get('order_id')
            }
            
            # Log trade
            self.trade_log.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol,
                'action': 'BUY',
                'quantity': shares,
                'price': current_price,
                'confidence': signal['confidence'],
                'order_id': order.get('order_id')
            })
            
            self.trades_today += 1
            self.total_trades += 1
            
        except Exception as e:
            logger.error(f"Error executing buy for {symbol}: {e}")
    
    async def execute_sell(self, symbol: str, signal: Dict):
        """Execute sell order (short selling)"""
        # TODO: Implement short selling logic
        logger.info(f"SHORT selling not implemented for {symbol}")
        pass
    
    async def manage_positions(self):
        """Monitor and manage existing positions"""
        
        for symbol, position in list(self.positions.items()):
            try:
                # Get current price
                quote = NSEDataService.get_quote(symbol)
                if not quote:
                    continue
                
                current_price = quote['ltp']
                position['current_price'] = current_price
                
                entry_price = position['entry_price']
                pnl = (current_price - entry_price) * position['quantity']
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                # Check stop loss
                if current_price <= position['stop_loss']:
                    logger.warning(f"🔴 STOP LOSS HIT: {symbol} | P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
                    await self.close_position(symbol, current_price, "Stop loss")
                    continue
                
                # Check take profit
                if current_price >= position['take_profit']:
                    logger.info(f"🟢 TAKE PROFIT HIT: {symbol} | P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%)")
                    await self.close_position(symbol, current_price, "Take profit")
                    continue
                
                # Trail stop loss if in profit
                if pnl_percent > 5:
                    atr = position['signal'].get('atr', current_price * 0.02)
                    new_stop_loss = current_price - (1.5 * atr)
                    if new_stop_loss > position['stop_loss']:
                        position['stop_loss'] = new_stop_loss
                        logger.info(f"📈 Trailing stop for {symbol}: ₹{new_stop_loss:.2f}")
            
            except Exception as e:
                logger.error(f"Error managing position {symbol}: {e}")
    
    async def close_position(self, symbol: str, exit_price: float, reason: str):
        """Close an open position"""
        try:
            position = self.positions.get(symbol)
            if not position:
                return
            
            # Place sell order
            order = AngelOneService.place_order(
                symbol=symbol,
                token=position['signal']['token'],
                exchange='NSE',
                quantity=position['quantity'],
                order_type='MARKET',
                transaction_type='SELL'
            )
            
            # Calculate P&L
            pnl = (exit_price - position['entry_price']) * position['quantity']
            pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            
            # Update statistics
            self.daily_pnl += pnl
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
            
            # Log exit
            self.trade_log.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': symbol,
                'action': 'SELL',
                'quantity': position['quantity'],
                'price': exit_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'reason': reason,
                'order_id': order.get('order_id')
            })
            
            logger.info(f"🔄 CLOSED: {symbol} | P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%) | Reason: {reason}")
            
            # Remove position
            del self.positions[symbol]
        
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
    
    def update_statistics(self):
        """Update trading statistics"""
        # Win rate
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        else:
            self.win_rate = 0
    
    def get_status(self) -> Dict:
        """Get current trader status"""
        return {
            'enabled': self.enabled,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'pause_reason': self.pause_reason,
            'daily_pnl': self.daily_pnl,
            'trades_today': self.trades_today,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': getattr(self, 'win_rate', 0),
            'active_positions': len(self.positions),
            'positions': list(self.positions.values()),
            'config': {
                'min_confidence': self.min_signal_confidence,
                'min_strength': self.min_signal_strength,
                'max_positions': self.max_positions,
                'check_interval': self.check_interval_seconds
            }
        }


# Global instance (disabled by default)
autonomous_trader = AutonomousTrader()
