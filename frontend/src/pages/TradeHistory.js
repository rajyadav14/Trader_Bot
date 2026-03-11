import { Card } from '@/components/ui/card';

export const TradeHistory = () => {
  return (
    <div className="p-4" data-testid="trade-history-page">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#E4E4E7]">Trade History</h1>
        <p className="text-sm text-[#52525B] mt-1">Complete audit trail of all executed trades</p>
      </div>

      <Card className="bg-[#0A0A0B] border-[#1F1F23] p-12 rounded-sm text-center">
        <p className="text-[#52525B]">No trade history yet</p>
        <p className="text-sm text-[#52525B] mt-2">
          Trade history will be logged here once the system starts executing orders
        </p>
      </Card>
    </div>
  );
};

export default TradeHistory;
