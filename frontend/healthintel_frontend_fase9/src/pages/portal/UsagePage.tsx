import { useEffect, useMemo, useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { UsageChart } from '../../components/charts/UsageChart';
import { LatencyChart } from '../../components/charts/LatencyChart';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, getUsageData } from '../../services/localPortalStore';
import { requestApi } from '../../services/apiClient';
import { getApiKey } from '../../services/storage';
import { useAuth } from '../../hooks/useAuth';
import type { UsageRealData } from '../../types/domain';

const periods = ['hoje', '7 dias', '30 dias', 'mês atual'] as const;
const periodoMap: Record<typeof periods[number], string> = {
  'hoje': 'hoje',
  '7 dias': '7d',
  '30 dias': '30d',
  'mês atual': 'mes_atual',
};

export function UsagePage() {
  const { user } = useAuth();
  const { success } = useNotification();
  const [period, setPeriod] = useState<typeof periods[number]>('7 dias');
  const [realData, setRealData] = useState<UsageRealData | null>(null);
  const [loadingReal, setLoadingReal] = useState(false);

  useEffect(() => {
    const key = getApiKey();
    if (!key?.trim()) return;
    setLoadingReal(true);
    requestApi('/v1/me/uso', { apiKey: key, query: { periodo: periodoMap[period] } })
      .then((res) => {
        if (res.ok && res.data) setRealData((res.data as { dados: UsageRealData }).dados);
        else setRealData(null);
      })
      .finally(() => setLoadingReal(false));
  }, [period]);

  const mockData = getUsageData();
  const mockFiltered = useMemo(() => {
    if (period === 'hoje') return mockData.slice(-1);
    if (period === '7 dias') return mockData.slice(-7);
    return mockData;
  }, [mockData, period]);

  const totalRequests = realData ? realData.total_requisicoes : mockFiltered.reduce((sum, item) => sum + item.requisicoes, 0);
  const totalErrors = realData ? realData.total_erros : mockFiltered.reduce((sum, item) => sum + item.erros, 0);
  const latency = realData ? realData.latencia_media_ms : Math.round(mockFiltered.reduce((sum, item) => sum + item.latenciaMs, 0) / Math.max(mockFiltered.length, 1));
  const isDemo = !realData;

  function exportReport(format: 'json' | 'csv') {
    const origem = isDemo ? 'demo local' : 'real';
    const payload = realData
      ? realData.serie_diaria.map((item) => ({ ...item, periodo: period, origem }))
      : mockFiltered.map((item) => ({ ...item, periodo: period, origem }));
    const latenciaKey = (item: Record<string, unknown>) =>
      'latencia_ms' in item ? item['latencia_ms'] : item['latenciaMs'];
    const content = format === 'json'
      ? JSON.stringify(payload, null, 2)
      : ['dia,requisicoes,erros,latencia_ms,periodo,origem', ...payload.map((item) => `${item.dia},${item.requisicoes},${item.erros},${latenciaKey(item as Record<string, unknown>)},${item.periodo},${item.origem}`)].join('\n');
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

      {isDemo && !getApiKey() && (
        <div className="empty-state-inline">
          Configure uma <strong>API key</strong> em <a href="/app/api-keys">API Keys</a> para ver dados reais de consumo. Exibindo dados demonstrativos.
        </div>
      )}
      <div className="metrics-grid">
        <MetricCard label="Requisições" value={loadingReal ? '…' : String(totalRequests)} detail={isDemo ? 'demonstrativo' : 'real'} />
        <MetricCard label="Erros" value={loadingReal ? '…' : String(totalErrors)} detail={isDemo ? 'demonstrativo' : 'real'} />
        <MetricCard label="Latência média" value={loadingReal ? '…' : `${latency} ms`} detail={isDemo ? 'demonstrativo' : 'real'} />
        <MetricCard label="Rate limit" value="60 rpm" detail="ajustável por plano" />
      </div>

      <Card>
        <CardHeader title="Filtros e exportação" description={isDemo ? 'Dados demonstrativos locais. Configure uma API key para ver consumo real.' : `Dados reais do plano ${user?.plano || ''}.`} />
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
