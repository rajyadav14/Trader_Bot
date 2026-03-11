import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'];

export const SignalFeed = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    try {
      const signalPromises = WATCHLIST.map(symbol => 
        axios.get(`${API}/signals/${symbol}`).catch(e => null)
      );
      
      const results = await Promise.all(signalPromises);
      const validSignals = results
        .filter(r => r && r.data)
        .map(r => r.data)
        .sort((a, b) => b.confidence - a.confidence);
      
      setSignals(validSignals);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching signals:', error);
      setLoading(false);
    }
  };

  const getDirectionIcon = (direction) => {
    switch (direction) {
      case 'BUY':
        return <TrendingUp className="w-4 h-4 text-[#00E396]" />;
      case 'SELL':
        return <TrendingDown className="w-4 h-4 text-[#FF0055]" />;
      default:
        return <Minus className="w-4 h-4 text-[#52525B]" />;
    }
  };

  const getDirectionColor = (direction) => {
    switch (direction) {
      case 'BUY':
        return 'text-[#00E396]';
      case 'SELL':
        return 'text-[#FF0055]';
      default:
        return 'text-[#52525B]';
    }
  };

  return (
    <Card className="bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="signal-feed">
      <h3 className="text-sm font-semibold text-[#E4E4E7] mb-3 uppercase tracking-wider">AI Signals</h3>
      
      <div className="space-y-1 max-h-[300px] overflow-y-auto">
        {loading ? (
          <div className="text-xs text-[#52525B] text-center py-4">Loading signals...</div>
        ) : signals.length === 0 ? (
          <div className="text-xs text-[#52525B] text-center py-4">No signals available</div>
        ) : (
          signals.map((signal, idx) => (
            <div
              key={`${signal.symbol}-${idx}`}
              className="signal-item p-2 border border-[#1F1F23] rounded-sm"
              data-testid={`signal-${signal.symbol}`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono font-medium text-[#E4E4E7]">{signal.symbol}</span>
                  {getDirectionIcon(signal.direction)}
                  <span className={`text-xs font-medium ${getDirectionColor(signal.direction)}`}>
                    {signal.direction}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[#52525B]">Strength:</span>
                  <span className="text-xs font-mono text-[#E4E4E7]">{signal.strength}/10</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#52525B]">Confidence: <span className="text-[#E4E4E7] font-mono">{signal.confidence.toFixed(0)}%</span></span>
                {signal.should_trade ? (
                  <span className="px-1.5 py-0.5 bg-[#00E396]/10 text-[#00E396] rounded-sm text-[10px] font-medium">TRADE</span>
                ) : (
                  <span className="px-1.5 py-0.5 bg-[#52525B]/10 text-[#52525B] rounded-sm text-[10px] font-medium">HOLD</span>
                )}
              </div>
              
              {signal.current_price && (
                <div className="mt-1 text-xs text-[#52525B]">
                  Price: <span className="text-[#E4E4E7] font-mono">${signal.current_price.toFixed(2)}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
