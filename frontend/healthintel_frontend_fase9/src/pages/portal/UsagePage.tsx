import { useMemo, useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { UsageChart } from '../../components/charts/UsageChart';
import { LatencyChart } from '../../components/charts/LatencyChart';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, getUsageData } from '../../services/localPortalStore';
import { useAuth } from '../../hooks/useAuth';

const periods = ['hoje', '7 dias', '30 dias', 'mês atual'] as const;

export function UsagePage() {
  const { user } = useAuth();
  const { success } = useNotification();
  const [period, setPeriod] = useState<typeof periods[number]>('7 dias');
  const data = getUsageData();
  const filtered = useMemo(() => {
    if (period === 'hoje') return data.slice(-1);
    if (period === '7 dias') return data.slice(-7);
    return data;
  }, [data, period]);
  const totalRequests = filtered.reduce((sum, item) => sum + item.requisicoes, 0);
  const totalErrors = filtered.reduce((sum, item) => sum + item.erros, 0);
  const latency = Math.round(filtered.reduce((sum, item) => sum + item.latenciaMs, 0) / Math.max(filtered.length, 1));

  function exportReport(format: 'json' | 'csv') {
    const payload = filtered.map((item) => ({ ...item, periodo: period, origem: 'demo local' }));
    const content = format === 'json'
      ? JSON.stringify(payload, null, 2)
      : ['dia,requisicoes,erros,latenciaMs,periodo,origem', ...payload.map((item) => `${item.dia},${item.requisicoes},${item.erros},${item.latenciaMs},${item.periodo},${item.origem}`)].join('\n');
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `healthintel_uso_${period.replaceAll(' ', '_')}.${format}`;
    anchor.click();
    URL.revokeObjectURL(url);
    addAuditEvent({
      tipo: 'uso_exportado',
      usuario: user?.email || 'portal_local',
      detalhe: `Relatorio ${format.toUpperCase()} gerado com dados demonstrativos locais.`,
      status: 'sucesso'
    });
    success('Relatório local gerado.');
  }

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
        <MetricCard label="Requisições" value={String(totalRequests)} detail="demo local" />
        <MetricCard label="Erros" value={String(totalErrors)} detail="demo local" />
        <MetricCard label="Latência média" value={`${latency} ms`} detail="demo local" />
        <MetricCard label="Rate limit" value="60 rpm" detail="ajustável por plano" />
      </div>

      <Card>
        <CardHeader title="Filtros e exportação" description="Sem endpoint real agregado de uso, estes dados permanecem demonstrativos locais." />
        <div className="button-row">
          {periods.map((item) => (
            <Button key={item} variant={item === period ? 'primary' : 'secondary'} onClick={() => setPeriod(item)}>
              {item}
            </Button>
          ))}
          <Button variant="secondary" onClick={() => exportReport('json')}>Exportar JSON</Button>
          <Button variant="secondary" onClick={() => exportReport('csv')}>Exportar CSV</Button>
        </div>
      </Card>

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
