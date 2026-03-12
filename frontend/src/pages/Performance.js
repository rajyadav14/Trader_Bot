import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { TrendingUp, Target, Award, Activity } from 'lucide-react';
import { EquityCurveChart } from '@/components/charts/EquityCurveChart';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/nse`;

export const Performance = () => {
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPerformance = async () => {
    try {
      const res = await axios.get(`${API}/performance`);
      setPerformance(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching performance:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-[#A1A1AA] text-sm">Loading...</div>
      </div>
    );
  }

  const totalPnl = performance?.total_pnl || 0;
  const totalPnlPercent = performance?.total_pnl_percent || 0;

  return (
    <div className="p-4" data-testid="performance-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#E4E4E7]">Performance Analytics</h1>
        <p className="text-sm text-[#52525B] mt-1">Comprehensive performance metrics and statistics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Total Return</p>
              <p className={`text-2xl font-mono font-medium ${
                totalPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {totalPnl >= 0 ? '+' : ''}₹{totalPnl.toFixed(2)}
              </p>
              <p className={`text-sm font-mono ${
                totalPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {totalPnlPercent >= 0 ? '+' : ''}{totalPnlPercent.toFixed(2)}%
              </p>
            </div>
            <div className={`w-10 h-10 rounded-sm flex items-center justify-center ${
              totalPnl >= 0 ? 'bg-[#00E396]/10' : 'bg-[#FF0055]/10'
            }`}>
              <TrendingUp className={`w-5 h-5 ${
                totalPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`} />
            </div>
          </div>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Sharpe Ratio</p>
              <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
                {performance?.sharpe_ratio?.toFixed(2) || '--'}
              </p>
              <p className="text-sm text-[#52525B]">Risk-adjusted return</p>
            </div>
            <div className="w-10 h-10 rounded-sm bg-[#00F0FF]/10 flex items-center justify-center">
              <Award className="w-5 h-5 text-[#00F0FF]" />
            </div>
          </div>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Max Drawdown</p>
              <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
                {performance?.max_drawdown ? `${performance.max_drawdown.toFixed(2)}%` : '--'}
              </p>
              <p className="text-sm text-[#52525B]">Peak to trough</p>
            </div>
            <div className="w-10 h-10 rounded-sm bg-[#FF0055]/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-[#FF0055]" />
            </div>
          </div>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-2">Win Rate</p>
              <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
                {performance?.win_rate ? `${performance.win_rate.toFixed(1)}%` : '--'}
              </p>
              <p className="text-sm text-[#52525B]">Winning trades</p>
            </div>
            <div className="w-10 h-10 rounded-sm bg-[#7000FF]/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-[#7000FF]" />
            </div>
          </div>
        </Card>
      </div>

      {/* Equity Curve */}
      <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm mb-6" style={{ height: '500px' }}>
        <h3 className="text-sm font-semibold text-[#E4E4E7] mb-4 uppercase tracking-wider">Equity Curve</h3>
        <EquityCurveChart equity={performance?.equity || 100000} />
      </Card>

      {/* Trade Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <h3 className="text-xs text-[#52525B] uppercase tracking-wider mb-4">Trade Statistics</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Total Trades</span>
              <span className="text-sm font-mono font-medium text-[#E4E4E7]">
                {performance?.total_trades || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Winning Trades</span>
              <span className="text-sm font-mono font-medium text-[#00E396]">
                {performance?.winning_trades || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Losing Trades</span>
              <span className="text-sm font-mono font-medium text-[#FF0055]">
                {performance?.losing_trades || 0}
              </span>
            </div>
          </div>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <h3 className="text-xs text-[#52525B] uppercase tracking-wider mb-4">Current Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Equity</span>
              <span className="text-sm font-mono font-medium text-[#E4E4E7]">
                ${performance?.equity?.toFixed(2) || '0.00'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Cash</span>
              <span className="text-sm font-mono font-medium text-[#E4E4E7]">
                ${performance?.cash?.toFixed(2) || '0.00'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Portfolio Value</span>
              <span className="text-sm font-mono font-medium text-[#E4E4E7]">
                ${performance?.portfolio_value?.toFixed(2) || '0.00'}
              </span>
            </div>
          </div>
        </Card>

        <Card className="bg-[#0A0A0B] border-[#1F1F23] p-4 rounded-sm">
          <h3 className="text-xs text-[#52525B] uppercase tracking-wider mb-4">Risk Metrics</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Daily P&L</span>
              <span className={`text-sm font-mono font-medium ${
                (performance?.daily_pnl || 0) >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {(performance?.daily_pnl || 0) >= 0 ? '+' : ''}${performance?.daily_pnl?.toFixed(2) || '0.00'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Daily P&L %</span>
              <span className={`text-sm font-mono font-medium ${
                (performance?.daily_pnl_percent || 0) >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {(performance?.daily_pnl_percent || 0) >= 0 ? '+' : ''}{performance?.daily_pnl_percent?.toFixed(2) || '0.00'}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#A1A1AA]">Status</span>
              <span className="text-sm font-medium text-[#00E396]">Active</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Performance;
