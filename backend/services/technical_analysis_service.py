import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd - macd_signal
        
        return {
            "macd": macd,
            "signal": macd_signal,
            "histogram": macd_histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            "upper": upper_band,
            "middle": sma,
            "lower": lower_band
        }
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def calculate_adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = TechnicalAnalysisService.calculate_atr(high, low, close, period)
        
        plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / tr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / tr)
        
        dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/period).mean()
        
        return adx
    
    @staticmethod
    def analyze_stock(
        df: pd.DataFrame,
        symbol: str
    ) -> Dict:
        """Comprehensive technical analysis"""
        try:
            if df.empty or len(df) < 50:
                return {"error": "Insufficient data"}
            
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate all indicators
            rsi = TechnicalAnalysisService.calculate_rsi(close)
            macd_data = TechnicalAnalysisService.calculate_macd(close)
            bb = TechnicalAnalysisService.calculate_bollinger_bands(close)
            sma_20 = TechnicalAnalysisService.calculate_sma(close, 20)
            sma_50 = TechnicalAnalysisService.calculate_sma(close, 50)
            sma_200 = TechnicalAnalysisService.calculate_sma(close, 200)
            ema_12 = TechnicalAnalysisService.calculate_ema(close, 12)
            ema_26 = TechnicalAnalysisService.calculate_ema(close, 26)
            atr = TechnicalAnalysisService.calculate_atr(high, low, close)
            obv = TechnicalAnalysisService.calculate_obv(close, volume)
            adx = TechnicalAnalysisService.calculate_adx(high, low, close)
            
            # Get latest values
            latest_idx = -1
            
            result = {
                "symbol": symbol,
                "current_price": float(close.iloc[latest_idx]),
                "rsi": float(rsi.iloc[latest_idx]) if not pd.isna(rsi.iloc[latest_idx]) else None,
                "macd": float(macd_data['macd'].iloc[latest_idx]) if not pd.isna(macd_data['macd'].iloc[latest_idx]) else None,
                "macd_signal": float(macd_data['signal'].iloc[latest_idx]) if not pd.isna(macd_data['signal'].iloc[latest_idx]) else None,
                "bollinger_upper": float(bb['upper'].iloc[latest_idx]) if not pd.isna(bb['upper'].iloc[latest_idx]) else None,
                "bollinger_middle": float(bb['middle'].iloc[latest_idx]) if not pd.isna(bb['middle'].iloc[latest_idx]) else None,
                "bollinger_lower": float(bb['lower'].iloc[latest_idx]) if not pd.isna(bb['lower'].iloc[latest_idx]) else None,
                "sma_20": float(sma_20.iloc[latest_idx]) if not pd.isna(sma_20.iloc[latest_idx]) else None,
                "sma_50": float(sma_50.iloc[latest_idx]) if not pd.isna(sma_50.iloc[latest_idx]) else None,
                "sma_200": float(sma_200.iloc[latest_idx]) if not pd.isna(sma_200.iloc[latest_idx]) else None,
                "ema_12": float(ema_12.iloc[latest_idx]) if not pd.isna(ema_12.iloc[latest_idx]) else None,
                "ema_26": float(ema_26.iloc[latest_idx]) if not pd.isna(ema_26.iloc[latest_idx]) else None,
                "atr": float(atr.iloc[latest_idx]) if not pd.isna(atr.iloc[latest_idx]) else None,
                "obv": float(obv.iloc[latest_idx]) if not pd.isna(obv.iloc[latest_idx]) else None,
                "adx": float(adx.iloc[latest_idx]) if not pd.isna(adx.iloc[latest_idx]) else None
            }
            
            # Generate signal
            signal = TechnicalAnalysisService._generate_signal(result)
            result["signal"] = signal
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _generate_signal(indicators: Dict) -> Dict:
        """Generate trading signal from indicators"""
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0
        reasons = []
        
        # RSI Analysis
        if indicators.get('rsi'):
            total_signals += 1
            if indicators['rsi'] < 30:
                bullish_signals += 1
                reasons.append("RSI oversold (<30)")
            elif indicators['rsi'] > 70:
                bearish_signals += 1
                reasons.append("RSI overbought (>70)")
        
        # MACD Analysis
        if indicators.get('macd') and indicators.get('macd_signal'):
            total_signals += 1
            if indicators['macd'] > indicators['macd_signal']:
                bullish_signals += 1
                reasons.append("MACD bullish crossover")
            else:
                bearish_signals += 1
                reasons.append("MACD bearish crossover")
        
        # Moving Average Analysis
        if indicators.get('sma_20') and indicators.get('sma_50'):
            total_signals += 1
            if indicators['sma_20'] > indicators['sma_50']:
                bullish_signals += 1
                reasons.append("SMA20 above SMA50")
            else:
                bearish_signals += 1
                reasons.append("SMA20 below SMA50")
        
        # Bollinger Bands Analysis
        if all([indicators.get('current_price'), indicators.get('bollinger_lower'), indicators.get('bollinger_upper')]):
            total_signals += 1
            price = indicators['current_price']
            if price < indicators['bollinger_lower']:
                bullish_signals += 1
                reasons.append("Price below lower Bollinger Band")
            elif price > indicators['bollinger_upper']:
                bearish_signals += 1
                reasons.append("Price above upper Bollinger Band")
        
        # Calculate signal metrics
        if total_signals > 0:
            bullish_pct = (bullish_signals / total_signals) * 100
            bearish_pct = (bearish_signals / total_signals) * 100
            confidence = max(bullish_pct, bearish_pct)
            
            if bullish_pct > bearish_pct:
                direction = "BUY"
                strength = min(10, int((bullish_pct / 10)))
            elif bearish_pct > bullish_pct:
                direction = "SELL"
                strength = min(10, int((bearish_pct / 10)))
            else:
                direction = "HOLD"
                strength = 5
        else:
            direction = "HOLD"
            strength = 5
            confidence = 50
            reasons = ["Insufficient indicators"]
        
        return {
            "direction": direction,
            "strength": strength,
            "confidence": confidence,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "total_signals": total_signals,
            "reasoning": "; ".join(reasons)
        }
