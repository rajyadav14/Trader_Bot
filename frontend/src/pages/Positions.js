import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/nse`;

export const Positions = () => {
  const [positions, setPositions] = useState([]);
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setRefreshing(true);
    try {
      const [positionsRes, accountRes] = await Promise.all([
        axios.get(`${API}/positions`),
        axios.get(`${API}/account`)
      ]);
      
      setPositions(positionsRes.data.positions);
      setAccount(accountRes.data);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error('Error fetching positions:', error);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const totalValue = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
  const totalPnl = positions.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0);

  return (
    <div className="p-4" data-testid="positions-page">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-[#E4E4E7]">Active Positions</h1>
          <p className="text-sm text-[#52525B] mt-1">Real-time position monitoring</p>
        </div>
        <Button
          onClick={fetchData}
          disabled={refreshing}
          className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90 rounded-sm"
          data-testid="refresh-positions-button"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Total Position Value</p>
          <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
            ₹{totalValue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </p>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Unrealized P&L</p>
          <p className={`text-2xl font-mono font-medium ${
            totalPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
          }`}>
            {totalPnl >= 0 ? '+' : ''}₹{totalPnl.toFixed(2)}
          </p>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Open Positions</p>
          <p className="text-2xl font-mono font-medium text-[#E4E4E7]">{positions.length}</p>
        </Card>
      </div>

      {/* Positions Table */}
      {loading ? (
        <div className="text-center py-12 text-[#52525B]">Loading positions...</div>
      ) : positions.length === 0 ? (
        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-12 rounded-sm text-center">
          <p className="text-[#52525B]">No open positions</p>
          <p className="text-sm text-[#52525B] mt-2">Positions will appear here when the system executes trades</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {positions.map((position, idx) => (
            <Card 
              key={`${position.symbol}-${idx}`}
              className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm hover:border-[#3F3F46] transition-colors"
              data-testid={`position-detail-${position.symbol}`}
            >
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Symbol & Side */}
                <div>
                  <p className="text-xl font-mono font-bold text-[#E4E4E7] mb-2">{position.symbol}</p>
                  <span className={`inline-block px-2 py-1 rounded-sm text-xs font-medium ${
                    position.side === 'BUY' 
                      ? 'bg-[#00E396]/10 text-[#00E396]' 
                      : 'bg-[#FF0055]/10 text-[#FF0055]'
                  }`}>
                    {position.side === 'BUY' ? 'LONG' : 'SHORT'} {position.qty} shares
                  </span>
                </div>

                {/* Entry & Current Price */}
                <div>
                  <div className="mb-3">
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Entry Price</p>
                    <p className="text-base font-mono font-medium text-[#E4E4E7]">
                      ${position.entry_price?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Current Price</p>
                    <p className="text-base font-mono font-medium text-[#E4E4E7]">
                      ${position.current_price?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                </div>

                {/* P&L */}
                <div>
                  <div className="mb-3">
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Unrealized P&L</p>
                    <p className={`text-base font-mono font-medium ${
                      (position.unrealized_pnl || 0) >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
                    }`}>
                      {(position.unrealized_pnl || 0) >= 0 ? '+' : ''}${position.unrealized_pnl?.toFixed(2) || '0.00'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">P&L %</p>
                    <p className={`text-base font-mono font-medium ${
                      (position.unrealized_pnl_percent || 0) >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
                    }`}>
                      {(position.unrealized_pnl_percent || 0) >= 0 ? '+' : ''}{position.unrealized_pnl_percent?.toFixed(2) || '0.00'}%
                    </p>
                  </div>
                </div>

                {/* Market Value */}
                <div>
                  <div>
                    <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Market Value</p>
                    <p className="text-base font-mono font-medium text-[#E4E4E7]">
                      ${position.market_value?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '0.00'}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Positions;
