import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { usageSeries } from '../../data/mock';

export function UsageChart() {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={usageSeries} margin={{ left: 0, right: 16, top: 16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dia" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="requisicoes" stroke="currentColor" fill="currentColor" fillOpacity={0.12} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
