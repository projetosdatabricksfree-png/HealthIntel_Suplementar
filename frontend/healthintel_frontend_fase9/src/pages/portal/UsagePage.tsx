import { useEffect, useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent } from '../../services/localPortalStore';
import { fetchJwt } from '../../services/apiClient';
import { useAuth } from '../../hooks/useAuth';
import type { UsageRealData, UsageMeta } from '../../types/domain';

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
  const [meta, setMeta] = useState<UsageMeta | null>(null);
  const [loadingReal, setLoadingReal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!user?.id) return;
    setLoadingReal(true);
    fetchJwt<{ dados: UsageRealData; meta: UsageMeta }>(
      '/v1/portal/dashboard/uso',
      { query: { periodo: periodoMap[period] } },
    )
      .then((payload) => {
        setRealData(payload.dados ?? null);
        setMeta(payload.meta ?? null);
      })
      .catch(() => {
        setRealData(null);
        setMeta(null);
      })
      .finally(() => setLoadingReal(false));
  }, [period, refreshKey, user?.id]);

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

  const quotaMonthly = meta?.quota_monthly ?? 0;
  const quotaUsedMonth = meta?.quota_used_month ?? 0;
  const quotaDaily = meta?.quota_daily ?? 0;
  const quotaUsedToday = meta?.quota_used_today ?? 0;
  const trialAtivo = Boolean(meta?.trial_pro_ativo);
  const trialExpiraEm = meta?.trial_pro_expira_em
    ? new Date(meta.trial_pro_expira_em).toLocaleDateString('pt-BR')
    : null;
  const modeloPayAsYouGo = meta?.modelo_cobranca === 'pay_as_you_go';

  const usoCotaPct = (() => {
    if (quotaMonthly > 0) {
      return Math.min(100, Math.round((quotaUsedMonth / quotaMonthly) * 100));
    }
    if (quotaDaily > 0) {
      return Math.min(100, Math.round((quotaUsedToday / quotaDaily) * 100));
    }
    return 0;
  })();

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Uso</p>
          <h1>Monitoramento de consumo</h1>
          <p>A API já registra logs de uso por cliente, chave, plano, endpoint, status e latência.</p>
        </div>
      </div>

      {trialAtivo && (
        <Card>
          <CardHeader
            title={(
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                <Sparkles size={16} /> Trial PRO ativo até {trialExpiraEm || '—'}
              </span>
            )}
            description="Durante o trial, sua chave responde com os limites do plano PRO (2.500 req/dia). Depois, volta ao plano FREE com 100 req/mês."
          />
        </Card>
      )}

      {modeloPayAsYouGo && (
        <Card>
          <CardHeader
            title="Plano Enterprise · pay-as-you-go"
            description="Sem cap diário ou mensal. Mínimo R$ 5.000/mês cobre 500.000 requisições; acima disso, R$ 50 por mil req. Fechamento mensal."
          />
        </Card>
      )}

      {(quotaMonthly > 0 || quotaDaily > 0) && !modeloPayAsYouGo && (
        <Card>
          <CardHeader
            title={quotaMonthly > 0 ? 'Cota mensal' : 'Cota diária'}
            description={
              quotaMonthly > 0
                ? `${quotaUsedMonth} de ${quotaMonthly} req usadas no mês corrente.`
                : `${quotaUsedToday} de ${quotaDaily} req usadas hoje (UTC-3).`
            }
          />
          <div
            style={{
              height: 8,
              borderRadius: 999,
              background: 'var(--surface-tint)',
              overflow: 'hidden',
              margin: '8px 0',
            }}
          >
            <div
              style={{
                width: `${usoCotaPct}%`,
                height: '100%',
                background:
                  usoCotaPct >= 90
                    ? 'var(--color-danger, #dc2626)'
                    : usoCotaPct >= 70
                    ? 'var(--color-warning, #f59e0b)'
                    : 'var(--primary)',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
          <p className="mono" style={{ fontSize: 11, color: 'var(--muted)', margin: 0 }}>
            {usoCotaPct}% utilizado · {quotaMonthly > 0
              ? `${quotaMonthly - quotaUsedMonth} restantes este mês`
              : `${quotaDaily - quotaUsedToday} restantes hoje`}
          </p>
        </Card>
      )}

      {!loadingReal && !hasRealData && (
        <div className="empty-state-inline">
          Ainda não há consumo real registrado para este tenant no período selecionado.{' '}
          <a href="/app/explorer">Faça uma chamada no Explorer</a> para ver dados aqui.
        </div>
      )}
      <div className="metrics-grid">
        <MetricCard label="Requisições no período" value={String(totalRequests)} detail={`período: ${period}`} loading={loadingReal} />
        <MetricCard label="Erros" value={String(totalErrors)} detail="4xx + 5xx" loading={loadingReal} />
        <MetricCard label="Latência média" value={`${latency} ms`} detail="real" loading={loadingReal} />
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
