import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { usageSeries } from '../../data/mock';

export function LatencyChart() {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={usageSeries} margin={{ left: 0, right: 16, top: 16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dia" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="latenciaMs" stroke="currentColor" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
