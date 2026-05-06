import { Card, CardHeader, MetricCard } from '../../components/Card';
import { UsageChart } from '../../components/charts/UsageChart';
import { LatencyChart } from '../../components/charts/LatencyChart';

export function UsagePage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Uso</p>
          <h1>Monitoramento de consumo</h1>
          <p>A API já registra logs de uso por cliente, chave, plano, endpoint, status e latência.</p>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Requisições/mês" value="6.430" detail="demo" />
        <MetricCard label="Erros" value="26" detail="0,4% demo" />
        <MetricCard label="Latência média" value="91 ms" detail="demo" />
        <MetricCard label="Rate limit" value="60 rpm" detail="ajustável por plano" />
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Requisições" description="Série demonstrativa." />
          <UsageChart />
        </Card>
        <Card>
          <CardHeader title="Latência" description="Série demonstrativa." />
          <LatencyChart />
        </Card>
      </div>
    </div>
  );
}
