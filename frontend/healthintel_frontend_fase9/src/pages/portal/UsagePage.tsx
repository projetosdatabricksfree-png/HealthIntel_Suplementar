import { useEffect, useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent } from '../../services/localPortalStore';
import { requestApi } from '../../services/apiClient';
import { getApiKey } from '../../services/storage';
import { useAuth } from '../../hooks/useAuth';
import type { UsageMeta, UsageRealData } from '../../types/domain';

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
  const [realMeta, setRealMeta] = useState<UsageMeta | null>(null);
  const [loadingReal, setLoadingReal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const key = getApiKey();
    if (!key?.trim()) return;
    setLoadingReal(true);
    requestApi('/v1/me/uso', { apiKey: key, query: { periodo: periodoMap[period] } })
      .then((res) => {
        if (res.ok && res.data) {
          const payload = res.data as { dados: UsageRealData; meta: UsageMeta };
          setRealData(payload.dados);
          setRealMeta(payload.meta);
        } else {
          setRealData(null);
          setRealMeta(null);
        }
      })
      .finally(() => setLoadingReal(false));
  }, [period, refreshKey]);

  useEffect(() => {
    const onUsageUpdated = () => setRefreshKey((n) => n + 1);
    window.addEventListener('usage-updated', onUsageUpdated);
    return () => window.removeEventListener('usage-updated', onUsageUpdated);
  }, []);

  const totalRequests = realData?.total_requisicoes ?? 0;
  const totalErrors = realData?.total_erros ?? 0;
  const latency = realData?.latencia_media_ms ?? 0;
  const hasRealData = Boolean(realData);

  function exportReport(format: 'json' | 'csv') {
    if (!realData) return;
    const origem = 'real';
    const payload = realData.serie_diaria.map((item) => ({ ...item, periodo: period, origem }));
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
      detalhe: `Relatorio ${format.toUpperCase()} gerado com dados reais.`,
      status: 'sucesso'
    });
    success('Relatório gerado.');
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

      {!getApiKey() && (
        <div className="empty-state-inline">
          Configure uma <strong>API key</strong> em <a href="/app/api-keys">API Keys</a> para ver dados reais de consumo.
        </div>
      )}
      {getApiKey() && !loadingReal && !hasRealData && (
        <div className="empty-state-inline">
          Ainda não há consumo real registrado para esta API key no período selecionado.{' '}
          <a href="/app/explorer">Faça uma chamada no Explorer</a> para ver dados aqui.
        </div>
      )}
      <div className="metrics-grid">
        <MetricCard label="Requisições" value={loadingReal ? '…' : String(totalRequests)} detail="real" />
        <MetricCard label="Erros" value={loadingReal ? '…' : String(totalErrors)} detail="4xx + 5xx" />
        <MetricCard label="Latência média" value={loadingReal ? '…' : `${latency} ms`} detail="real" />
        <MetricCard
          label="Quota diária"
          value={
            realMeta?.quota_daily
              ? `${realMeta.quota_used_today ?? 0}/${realMeta.quota_daily}`
              : '—'
          }
          detail={realMeta?.quota_daily ? `plano ${realMeta.plano}` : 'sem limite diário'}
        />
      </div>

      <Card>
        <CardHeader title="Filtros e exportação" description={`Dados reais do plano ${user?.tenant_ativo?.plano_nome || ''}.`} />
        <div className="button-row">
          {periods.map((item) => (
            <Button key={item} variant={item === period ? 'primary' : 'secondary'} onClick={() => setPeriod(item)}>
              {item}
            </Button>
          ))}
          <Button variant="secondary" disabled={!hasRealData} onClick={() => exportReport('json')}>Exportar JSON</Button>
          <Button variant="secondary" disabled={!hasRealData} onClick={() => exportReport('csv')}>Exportar CSV</Button>
        </div>
      </Card>

      {hasRealData ? (
        <div className="split-grid">
          <Card>
            <CardHeader title="Requisições" description="Série real retornada por /me/uso." />
            <div className="table-wrap">
              <table>
                <thead><tr><th>Dia</th><th>Requisições</th><th>Erros</th><th>Latência média</th></tr></thead>
                <tbody>
                  {realData?.serie_diaria.map((item) => (
                    <tr key={item.dia}>
                      <td>{item.dia}</td>
                      <td>{item.requisicoes}</td>
                      <td>{item.erros}</td>
                      <td>{item.latencia_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
          <Card>
            <CardHeader title="Top endpoints" description="Consumo agregado por endpoint." />
            <div className="table-wrap">
              <table>
                <thead><tr><th>Endpoint</th><th>Requisições</th><th>Erros</th></tr></thead>
                <tbody>
                  {realData?.por_endpoint.map((item) => (
                    <tr key={item.endpoint}>
                      <td><code>{item.endpoint}</code></td>
                      <td>{item.requisicoes}</td>
                      <td>{item.erros}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
