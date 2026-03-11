from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
from datetime import datetime, timezone
from typing import Dict, List
import logging
import random

logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    """Service for AI-powered sentiment analysis using GPT-5.2"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    def analyze_news_sentiment(self, symbol: str, news_text: str) -> Dict:
        """Analyze news sentiment using GPT-5.2"""
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"sentiment_{symbol}_{datetime.now(timezone.utc).timestamp()}",
                system_message="""You are a financial sentiment analyst. 
                Analyze the provided news text and provide:
                1. Sentiment score from -100 (extremely bearish) to +100 (extremely bullish)
                2. Key entities mentioned (companies, products, events)
                3. Impact magnitude (low, medium, high)
                4. Trading recommendation (BUY, SELL, HOLD)
                5. Brief reasoning
                
                Respond in JSON format:
                {
                  "sentiment_score": <number>,
                  "entities": [<list of strings>],
                  "impact": "<low|medium|high>",
                  "recommendation": "<BUY|SELL|HOLD>",
                  "reasoning": "<string>"
                }"""
            ).with_model("openai", "gpt-5.2")
            
            message = UserMessage(
                text=f"Analyze sentiment for {symbol}:\n\n{news_text}"
            )
            
            response = chat.send_message(message)
            
            # Parse response (in production, use json.loads)
            # For now, return structured format
            return self._parse_sentiment_response(response, symbol)
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return self._get_default_sentiment(symbol)
    
    def _parse_sentiment_response(self, response: str, symbol: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            import json
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                sentiment_score = data.get('sentiment_score', 0)
                
                # Convert to signal format
                if sentiment_score > 30:
                    direction = "BUY"
                    strength = min(10, int((sentiment_score + 100) / 20))
                elif sentiment_score < -30:
                    direction = "SELL"
                    strength = min(10, int((abs(sentiment_score) + 100) / 20))
                else:
                    direction = "HOLD"
                    strength = 5
                
                confidence = min(100, abs(sentiment_score) + 50)
                
                return {
                    "symbol": symbol,
                    "layer": "sentiment",
                    "direction": direction,
                    "strength": strength,
                    "confidence": confidence,
                    "sentiment_score": sentiment_score,
                    "entities": data.get('entities', []),
                    "impact": data.get('impact', 'medium'),
                    "reasoning": data.get('reasoning', 'No reasoning provided')
                }
            
            return self._get_default_sentiment(symbol)
        
        except Exception as e:
            logger.error(f"Error parsing sentiment response: {e}")
            return self._get_default_sentiment(symbol)
    
    def _get_default_sentiment(self, symbol: str) -> Dict:
        """Return default sentiment when analysis fails"""
        return {
            "symbol": symbol,
            "layer": "sentiment",
            "direction": "HOLD",
            "strength": 5,
            "confidence": 50,
            "sentiment_score": 0,
            "entities": [],
            "impact": "low",
            "reasoning": "Unable to analyze sentiment"
        }
    
    def get_mock_news(self, symbol: str) -> str:
        """Generate mock news for testing"""
        mock_news_templates = [
            f"{symbol} reports strong quarterly earnings, beating analyst expectations by 15%. Revenue up 22% YoY.",
            f"{symbol} announces new product line expected to drive significant growth in next quarter.",
            f"Analysts downgrade {symbol} citing increased competition and margin pressure.",
            f"{symbol} CEO steps down amid controversy, interim leadership appointed.",
            f"Major institutional investor increases stake in {symbol} by 12%, signaling confidence.",
            f"{symbol} faces regulatory scrutiny over recent business practices.",
            f"Industry tailwinds benefit {symbol} as sector demand reaches all-time high.",
            f"{symbol} announces strategic acquisition to expand market presence."
        ]
        
        return random.choice(mock_news_templates)
    
    def analyze_symbol_sentiment(self, symbol: str) -> Dict:
        """Complete sentiment analysis for a symbol"""
        # Get mock news
        news = self.get_mock_news(symbol)
        
        # Analyze sentiment
        result = self.analyze_news_sentiment(symbol, news)
        result["news_text"] = news
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return result
