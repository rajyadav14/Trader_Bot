import { useEffect, useState } from 'react';
import axios from 'axios';
import { ArrowUpRight, ArrowDownRight, TrendingUp, DollarSign, Target, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { EquityCurveChart } from '@/components/charts/EquityCurveChart';
import { AIBrainVisualization } from '@/components/AIBrainVisualization';
import { SignalFeed } from '@/components/SignalFeed';
import { PositionsTable } from '@/components/PositionsTable';
import { RiskMetrics } from '@/components/RiskMetrics';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/nse`; // Changed to NSE endpoints

export const Dashboard = () => {
  const [account, setAccount] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [accountRes, performanceRes, positionsRes] = await Promise.all([
        axios.get(`${API}/account`),
        axios.get(`${API}/performance`),
        axios.get(`${API}/positions`)
      ]);

      setAccount(accountRes.data);
      setPerformance(performanceRes.data);
      setPositions(positionsRes.data.positions);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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

  const dailyPnl = performance?.daily_pnl || 0;
  const dailyPnlPercent = performance?.daily_pnl_percent || 0;
  const totalPnl = performance?.total_pnl || 0;
  const totalPnlPercent = performance?.total_pnl_percent || 0;

  return (
    <div className="p-4 space-y-1">
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-1">
        {/* Equity */}
        <Card className="stat-card bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="equity-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Equity</p>
              <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
                ₹{performance?.equity?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
              </p>
            </div>
            <div className="w-10 h-10 rounded-sm bg-[#00F0FF]/10 flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-[#00F0FF]" />
            </div>
          </div>
        </Card>

        {/* Daily P&L */}
        <Card className="stat-card bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="daily-pnl-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Daily P&L</p>
              <p className={`text-2xl font-mono font-medium ${
                dailyPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {dailyPnl >= 0 ? '+' : ''}{dailyPnl.toFixed(2)}
              </p>
              <p className={`text-xs font-mono ${
                dailyPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {dailyPnlPercent >= 0 ? '+' : ''}{dailyPnlPercent.toFixed(2)}%
              </p>
            </div>
            <div className={`w-10 h-10 rounded-sm flex items-center justify-center ${
              dailyPnl >= 0 ? 'bg-[#00E396]/10' : 'bg-[#FF0055]/10'
            }`}>
              {dailyPnl >= 0 ? (
                <ArrowUpRight className="w-5 h-5 text-[#00E396]" />
              ) : (
                <ArrowDownRight className="w-5 h-5 text-[#FF0055]" />
              )}
            </div>
          </div>
        </Card>

        {/* Total P&L */}
        <Card className="stat-card bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="total-pnl-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Total P&L</p>
              <p className={`text-2xl font-mono font-medium ${
                totalPnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
              }`}>
                {totalPnl >= 0 ? '+' : ''}{totalPnl.toFixed(2)}
              </p>
              <p className={`text-xs font-mono ${
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

        {/* Buying Power */}
        <Card className="stat-card bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="buying-power-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-[#52525B] uppercase tracking-wider mb-1">Buying Power</p>
              <p className="text-2xl font-mono font-medium text-[#E4E4E7]">
                ₹{account?.funds?.available_cash?.toLocaleString('en-IN', { minimumFractionDigits: 0 }) || '0'}
              </p>
            </div>
            <div className="w-10 h-10 rounded-sm bg-[#7000FF]/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-[#7000FF]" />
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-1">
        {/* Left Column - Equity Curve */}
        <div className="lg:col-span-2">
          <Card className="bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm h-[400px]" data-testid="equity-curve-chart">
            <h3 className="text-sm font-semibold text-[#E4E4E7] mb-3 uppercase tracking-wider">Equity Curve</h3>
            <EquityCurveChart equity={performance?.equity || 100000} />
          </Card>
        </div>

        {/* Right Column - AI Brain */}
        <div>
          <Card className="bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm h-[400px]" data-testid="ai-brain-visualization">
            <h3 className="text-sm font-semibold text-[#E4E4E7] mb-3 uppercase tracking-wider">AI Brain</h3>
            <AIBrainVisualization />
          </Card>
        </div>
      </div>

      {/* Signal Feed & Positions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-1">
        <SignalFeed />
        <PositionsTable positions={positions} />
      </div>

      {/* Risk Metrics */}
      <RiskMetrics account={account} positions={positions} />
    </div>
  );
};

export default Dashboard;
