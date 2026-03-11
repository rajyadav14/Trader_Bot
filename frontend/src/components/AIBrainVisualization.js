export const AIBrainVisualization = () => {
  const layers = [
    { name: 'Technical', status: 'active', confidence: 78 },
    { name: 'Sentiment', status: 'active', confidence: 65 },
    { name: 'Quantitative', status: 'idle', confidence: 0 },
    { name: 'Macro', status: 'idle', confidence: 0 },
    { name: 'Prediction', status: 'idle', confidence: 0 }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#00E396';
      case 'processing':
        return '#FFD600';
      case 'idle':
        return '#52525B';
      default:
        return '#52525B';
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center space-y-6">
      {/* Central Node */}
      <div className="relative">
        <div className="w-24 h-24 rounded-full bg-[#00F0FF]/10 border-2 border-[#00F0FF] flex items-center justify-center">
          <div className="text-center">
            <div className="text-xs text-[#52525B] uppercase tracking-wider">Fusion</div>
            <div className="text-lg font-mono font-bold text-[#00F0FF]">72%</div>
          </div>
        </div>
        
        {/* Pulsating effect */}
        <div className="absolute inset-0 w-24 h-24 rounded-full border-2 border-[#00F0FF] animate-ping opacity-20"></div>
      </div>

      {/* Layer Nodes */}
      <div className="grid grid-cols-2 gap-4 w-full max-w-xs">
        {layers.slice(0, 4).map((layer, idx) => (
          <div
            key={layer.name}
            className="flex flex-col items-center justify-center p-3 bg-[#0F0F12] border border-[#1F1F23] rounded-sm"
            data-testid={`ai-layer-${layer.name.toLowerCase()}`}
          >
            <div 
              className="w-3 h-3 rounded-full mb-2" 
              style={{ backgroundColor: getStatusColor(layer.status) }}
            />
            <div className="text-xs text-[#A1A1AA] text-center uppercase tracking-wider">{layer.name}</div>
            {layer.confidence > 0 && (
              <div className="text-xs font-mono text-[#E4E4E7] mt-1">{layer.confidence}%</div>
            )}
          </div>
        ))}
      </div>

      {/* Status */}
      <div className="text-center">
        <div className="text-xs text-[#52525B] uppercase tracking-wider">System Status</div>
        <div className="text-sm text-[#00E396] font-medium mt-1">Active</div>
      </div>
    </div>
  );
};
