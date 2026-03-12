import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/nse`;

const WATCHLIST = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'HINDUNILVR'];

export const Signals = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    setRefreshing(true);
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
      setRefreshing(false);
    } catch (error) {
      console.error('Error fetching signals:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getDirectionIcon = (direction) => {
    switch (direction) {
      case 'BUY':
        return <TrendingUp className="w-5 h-5 text-[#00E396]" />;
      case 'SELL':
        return <TrendingDown className="w-5 h-5 text-[#FF0055]" />;
      default:
        return <Minus className="w-5 h-5 text-[#52525B]" />;
    }
  };

  const getDirectionColor = (direction) => {
    switch (direction) {
      case 'BUY':
        return 'text-[#00E396] bg-[#00E396]/10';
      case 'SELL':
        return 'text-[#FF0055] bg-[#FF0055]/10';
      default:
        return 'text-[#52525B] bg-[#52525B]/10';
    }
  };

  return (
    <div className="p-4" data-testid="signals-page">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#E4E4E7]">AI Trading Signals</h1>
          <p className="text-sm text-[#52525B] mt-1">Real-time analysis from multiple AI layers</p>
        </div>
        <Button
          onClick={fetchSignals}
          disabled={refreshing}
          className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90 rounded-sm"
          data-testid="refresh-signals-button"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-[#52525B]">Loading signals...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {signals.map((signal, idx) => (
            <Card 
              key={`${signal.symbol}-${idx}`} 
              className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm hover:border-[#3F3F46] transition-colors"
              data-testid={`signal-card-${signal.symbol}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getDirectionIcon(signal.direction)}
                  <div>
                    <h3 className="text-xl font-mono font-bold text-[#E4E4E7]">{signal.symbol}</h3>
                    <span className={`inline-block px-2 py-1 rounded-sm text-xs font-medium mt-1 ${getDirectionColor(signal.direction)}`}>
                      {signal.direction}
                    </span>
                  </div>
                </div>
                {signal.should_trade && (
                  <span className="px-2 py-1 bg-[#00E396]/10 text-[#00E396] rounded-sm text-xs font-medium border border-[#00E396]/20">
                    TRADE SIGNAL
                  </span>
                )}
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div>
                  <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Strength</p>
                  <p className="text-lg font-mono font-medium text-[#E4E4E7]">{signal.strength}/10</p>
                </div>
                <div>
                  <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Confidence</p>
                  <p className="text-lg font-mono font-medium text-[#E4E4E7]">{signal.confidence.toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Consensus</p>
                  <p className="text-lg font-mono font-medium text-[#E4E4E7]">{signal.consensus?.toFixed(0) || 0}%</p>
                </div>
              </div>

              {/* Price & Position */}
              {signal.current_price && (
                <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-[#0F0F12] border border-[#1F1F23] rounded-sm">
                  <div>
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Current Price</p>
                    <p className="text-base font-mono font-medium text-[#E4E4E7]">₹{signal.current_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Rec. Shares</p>
                    <p className="text-base font-mono font-medium text-[#E4E4E7]">{signal.recommended_shares || 0}</p>
                  </div>
                </div>
              )}

              {/* Layer Signals */}
              <div className="space-y-2">
                <p className="text-xs text-[#52525B] uppercase tracking-wider">Layer Analysis</p>
                {signal.layer_signals?.map((layer, layerIdx) => (
                  <div 
                    key={layerIdx}
                    className="flex items-center justify-between p-2 bg-[#0F0F12] border border-[#1F1F23] rounded-sm text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-[#A1A1AA] uppercase">{layer.layer}</span>
                      <span className={`px-1.5 py-0.5 rounded-sm font-medium ${
                        layer.direction === 'BUY' ? 'bg-[#00E396]/10 text-[#00E396]' :
                        layer.direction === 'SELL' ? 'bg-[#FF0055]/10 text-[#FF0055]' :
                        'bg-[#52525B]/10 text-[#52525B]'
                      }`}>
                        {layer.direction}
                      </span>
                    </div>
                    <span className="font-mono text-[#E4E4E7]">{layer.confidence?.toFixed(0) || 0}%</span>
                  </div>
                ))}
              </div>

              {/* Reasoning */}
              {signal.reasoning && (
                <div className="mt-4 pt-4 border-t border-[#1F1F23]">
                  <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Analysis</p>
                  <p className="text-xs text-[#A1A1AA] leading-relaxed">{signal.reasoning}</p>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Signals;
