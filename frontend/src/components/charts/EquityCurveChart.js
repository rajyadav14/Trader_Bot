import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from 'react';

export const EquityCurveChart = ({ equity }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Generate mock equity curve data
    const generateData = () => {
      const points = [];
      const startingEquity = 100000;
      let currentEquity = startingEquity;
      
      for (let i = 0; i <= 30; i++) {
        const date = new Date();
        date.setDate(date.getDate() - (30 - i));
        
        // Random walk towards current equity
        const volatility = 0.015;
        const drift = (equity - startingEquity) / 30;
        const change = drift + (Math.random() - 0.5) * currentEquity * volatility;
        currentEquity += change;
        
        points.push({
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          equity: parseFloat(currentEquity.toFixed(2))
        });
      }
      
      // Ensure last point matches current equity
      points[points.length - 1].equity = equity;
      
      return points;
    };

    setData(generateData());
  }, [equity]);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" />
        <XAxis 
          dataKey="date" 
          stroke="#52525B" 
          tick={{ fill: '#52525B', fontSize: 10 }}
          tickLine={false}
        />
        <YAxis 
          stroke="#52525B" 
          tick={{ fill: '#52525B', fontSize: 10 }}
          tickLine={false}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: '#0A0A0B',
            border: '1px solid #3F3F46',
            borderRadius: '2px',
            fontSize: '12px'
          }}
          labelStyle={{ color: '#E4E4E7' }}
          itemStyle={{ color: '#00F0FF' }}
          formatter={(value) => [`$${value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Equity']}
        />
        <Line 
          type="monotone" 
          dataKey="equity" 
          stroke="#00F0FF" 
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: '#00F0FF' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
