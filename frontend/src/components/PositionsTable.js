import { Card } from '@/components/ui/card';

export const PositionsTable = ({ positions }) => {
  return (
    <Card className="bg-[#0A0A0B] border-[#1F1F23] p-3 rounded-sm" data-testid="positions-table">
      <h3 className="text-sm font-semibold text-[#E4E4E7] mb-3 uppercase tracking-wider">Active Positions</h3>
      
      {positions.length === 0 ? (
        <div className="text-xs text-[#52525B] text-center py-8">No active positions</div>
      ) : (
        <div className="space-y-1 max-h-[300px] overflow-y-auto">
          {positions.map((position, idx) => (
            <div
              key={`${position.symbol}-${idx}`}
              className="position-row p-2 border border-[#1F1F23] rounded-sm"
              data-testid={`position-${position.symbol}`}
            >
              <div className="flex items-center justify-between mb-1">
                <div>
                  <span className="text-sm font-mono font-medium text-[#E4E4E7]">{position.symbol}</span>
                  <span className={`ml-2 text-xs px-1.5 py-0.5 rounded-sm ${
                    position.side === 'BUY' 
                      ? 'bg-[#00E396]/10 text-[#00E396]' 
                      : 'bg-[#FF0055]/10 text-[#FF0055]'
                  }`}>
                    {position.side === 'BUY' ? 'LONG' : 'SHORT'}
                  </span>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-mono font-medium ${
                    position.unrealized_pnl >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
                  }`}>
                    {position.unrealized_pnl >= 0 ? '+' : ''}{position.unrealized_pnl?.toFixed(2) || '0.00'}
                  </div>
                  <div className={`text-xs font-mono ${
                    position.unrealized_pnl_percent >= 0 ? 'text-[#00E396]' : 'text-[#FF0055]'
                  }`}>
                    {position.unrealized_pnl_percent >= 0 ? '+' : ''}{position.unrealized_pnl_percent?.toFixed(2) || '0.00'}%
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-[#52525B]">Qty:</span>
                  <span className="text-[#E4E4E7] font-mono ml-1">{position.qty}</span>
                </div>
                <div>
                  <span className="text-[#52525B]">Entry:</span>
                  <span className="text-[#E4E4E7] font-mono ml-1">${position.entry_price?.toFixed(2) || '0.00'}</span>
                </div>
                <div>
                  <span className="text-[#52525B]">Current:</span>
                  <span className="text-[#E4E4E7] font-mono ml-1">${position.current_price?.toFixed(2) || '0.00'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
