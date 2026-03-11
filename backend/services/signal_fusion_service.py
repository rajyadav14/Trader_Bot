from typing import List, Dict
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class SignalFusionService:
    """Service for fusing signals from multiple AI layers"""
    
    # Minimum confidence threshold to consider trading
    MIN_CONFIDENCE = 72.0
    MIN_SIGNAL_STRENGTH = 7
    
    @staticmethod
    def fuse_signals(
        technical_signal: Dict,
        sentiment_signal: Dict,
        symbol: str
    ) -> Dict:
        """Fuse signals from multiple AI layers"""
        try:
            signals = [technical_signal, sentiment_signal]
            
            # Count direction votes
            buy_votes = sum(1 for s in signals if s.get('direction') == 'BUY')
            sell_votes = sum(1 for s in signals if s.get('direction') == 'SELL')
            hold_votes = sum(1 for s in signals if s.get('direction') == 'HOLD')
            
            total_votes = len(signals)
            
            # Calculate consensus
            max_votes = max(buy_votes, sell_votes, hold_votes)
            consensus = (max_votes / total_votes) * 100
            
            # Determine fused direction
            if buy_votes > sell_votes and buy_votes > hold_votes:
                direction = "BUY"
            elif sell_votes > buy_votes and sell_votes > hold_votes:
                direction = "SELL"
            else:
                direction = "HOLD"
            
            # Calculate weighted strength and confidence
            total_strength = sum(s.get('strength', 5) for s in signals)
            avg_strength = total_strength / total_votes
            
            total_confidence = sum(s.get('confidence', 50) for s in signals)
            avg_confidence = total_confidence / total_votes
            
            # Determine if should trade
            should_trade = (
                avg_confidence >= SignalFusionService.MIN_CONFIDENCE and
                avg_strength >= SignalFusionService.MIN_SIGNAL_STRENGTH and
                direction in ["BUY", "SELL"]
            )
            
            # Generate reasoning
            reasoning_parts = []
            for signal in signals:
                layer = signal.get('layer', 'unknown')
                sig_dir = signal.get('direction', 'HOLD')
                sig_conf = signal.get('confidence', 0)
                sig_reason = signal.get('reasoning', '')
                reasoning_parts.append(f"{layer.upper()}: {sig_dir} ({sig_conf:.0f}% conf) - {sig_reason}")
            
            reasoning = " | ".join(reasoning_parts)
            
            return {
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
                "reasoning": reasoning,
                "layer_signals": signals
            }
        
        except Exception as e:
            logger.error(f"Error fusing signals for {symbol}: {e}")
            return {
                "symbol": symbol,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "direction": "HOLD",
                "strength": 0,
                "confidence": 0,
                "consensus": 0,
                "should_trade": False,
                "error": str(e)
            }
    
    @staticmethod
    def calculate_position_size(
        account_equity: float,
        signal_strength: float,
        signal_confidence: float,
        max_position_pct: float = 5.0
    ) -> float:
        """Calculate position size using Kelly Criterion (fractional)"""
        try:
            # Simplified Kelly: f = (p * b - q) / b
            # Where p = probability of win, q = probability of loss, b = win/loss ratio
            
            # Convert confidence to probability
            win_prob = signal_confidence / 100.0
            loss_prob = 1 - win_prob
            
            # Assume 1.5:1 reward/risk ratio
            win_loss_ratio = 1.5
            
            # Kelly fraction
            kelly_fraction = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
            
            # Use 0.25x fractional Kelly for safety
            fractional_kelly = max(0, kelly_fraction * 0.25)
            
            # Adjust by signal strength (1-10 scale)
            strength_multiplier = signal_strength / 10.0
            
            # Calculate position percentage
            position_pct = fractional_kelly * strength_multiplier * 100
            
            # Cap at max position size
            position_pct = min(position_pct, max_position_pct)
            
            # Calculate dollar amount
            position_size = (position_pct / 100.0) * account_equity
            
            return round(position_size, 2)
        
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
