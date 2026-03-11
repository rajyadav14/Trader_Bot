import { Card } from '@/components/ui/card';
import { Shield, AlertTriangle, TrendingDown } from 'lucide-react';

export const RiskMetrics = ({ account, positions }) => {
  const dailyLossLimit = 2000; // -2% of $100k
  const dailyLoss = Math.abs(Math.min(0, account?.daily_pnl || 0));
  const dailyLossPercent = (dailyLoss / dailyLossLimit) * 100;
  
  const totalExposure = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
  const exposurePercent = account?.equity ? (totalExposure / account.equity) * 100 : 0;

  return (
    <Card className="bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="risk-metrics">
      <h3 className="text-sm font-semibold text-[#E4E4E7] mb-3 uppercase tracking-wider">Risk Management</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Daily Loss Limit */}
        <div className="p-3 bg-[#0F0F12] border border-[#1F1F23] rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#52525B] uppercase tracking-wider">Daily Loss</span>
            <TrendingDown className={`w-4 h-4 ${
              dailyLossPercent > 80 ? 'text-[#FF0055]' : 
              dailyLossPercent > 50 ? 'text-[#FFD600]' : 'text-[#00E396]'
            }`} />
          </div>
          <div className="text-lg font-mono font-medium text-[#E4E4E7] mb-1">
            ${dailyLoss.toFixed(2)}
          </div>
          <div className="w-full bg-[#1F1F23] rounded-full h-1.5 mb-1">
            <div 
              className={`h-1.5 rounded-full ${
                dailyLossPercent > 80 ? 'bg-[#FF0055]' : 
                dailyLossPercent > 50 ? 'bg-[#FFD600]' : 'bg-[#00E396]'
              }`}
              style={{ width: `${Math.min(100, dailyLossPercent)}%` }}
            />
          </div>
          <div className="text-xs text-[#52525B]">
            Limit: ${dailyLossLimit.toFixed(2)} ({dailyLossPercent.toFixed(0)}%)
          </div>
        </div>

        {/* Total Exposure */}
        <div className="p-3 bg-[#0F0F12] border border-[#1F1F23] rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#52525B] uppercase tracking-wider">Exposure</span>
            <Shield className="w-4 h-4 text-[#00F0FF]" />
          </div>
          <div className="text-lg font-mono font-medium text-[#E4E4E7] mb-1">
            ${totalExposure.toFixed(2)}
          </div>
          <div className="text-xs text-[#52525B]">
            {exposurePercent.toFixed(1)}% of equity
          </div>
        </div>

        {/* Max Drawdown */}
        <div className="p-3 bg-[#0F0F12] border border-[#1F1F23] rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[#52525B] uppercase tracking-wider">Max Drawdown</span>
            <AlertTriangle className="w-4 h-4 text-[#FFD600]" />
          </div>
          <div className="text-lg font-mono font-medium text-[#E4E4E7] mb-1">
            --
          </div>
          <div className="text-xs text-[#52525B]">
            Not yet calculated
          </div>
        </div>
      </div>
    </Card>
  );
};
