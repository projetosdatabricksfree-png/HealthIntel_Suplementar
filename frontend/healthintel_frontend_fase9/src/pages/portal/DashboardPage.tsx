import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, AlertCircle, AlertTriangle, BarChart3, BookOpen, CreditCard, Database, KeyRound, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { OnboardingChecklist } from '../../components/portal/OnboardingChecklist';
import { UsageChart } from '../../components/charts/UsageChart';
import { useAuth } from '../../hooks/useAuth';
import { requestApi } from '../../services/apiClient';
import { getApiKey } from '../../services/storage';
import { getCurrentPlan, hasPlanAtLeast } from '../../data/planRules';
import type { UsageMeta } from '../../types/domain';

export function DashboardPage() {
  const { user } = useAuth();
  const [apiStatus, setApiStatus] = useState<'loading' | 'ok' | 'error'>('loading');
  const [usageMeta, setUsageMeta] = useState<UsageMeta | null>(null);
  const [loadingUsage, setLoadingUsage] = useState<boolean>(false);
  const currentPlan = getCurrentPlan(user?.tenant_ativo?.plano_nome);
  const hasApiKey = Boolean(getApiKey().trim());

  useEffect(() => {
    requestApi('/saude', { apiKey: '' }).then((res) => setApiStatus(res.ok ? 'ok' : 'error'));
  }, []);

  useEffect(() => {
    const key = getApiKey();
    if (!key?.trim()) return;
    setLoadingUsage(true);
    requestApi('/v1/me/uso', { apiKey: key, query: { periodo: 'hoje' } })
      .then((res) => {
        if (res.ok && res.data) {
          const payload = res.data as { meta: UsageMeta };
          setUsageMeta(payload.meta ?? null);
        }
      })
      .finally(() => setLoadingUsage(false));
  }, []);

  const quotaUsed = usageMeta?.quota_used_today ?? null;
  const quotaDaily = usageMeta?.quota_daily ?? null;
  const quotaPct = quotaUsed !== null && quotaDaily ? Math.round((quotaUsed / quotaDaily) * 100) : null;
  const quotaWarning = quotaPct !== null && quotaPct >= 80 && quotaPct < 100;
  const quotaExceeded = quotaPct !== null && quotaPct >= 100;
  const hasUsage = quotaUsed !== null && quotaUsed > 0;

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>Bem-vindo, {user?.nome}</h1>
          <p>Visão operacional do seu consumo e acesso à API HealthIntel Core ANS.</p>
        </div>
        {!hasPlanAtLeast(currentPlan.slug, 'pro') && (
          <Link to="/app/billing" className="btn btn--primary">Fazer upgrade</Link>
        )}
      </div>

      <OnboardingChecklist hasApiKey={hasApiKey} hasUsage={hasUsage} />

      {(quotaWarning || quotaExceeded) && (
        <div className={`portal-alert portal-alert--${quotaExceeded ? 'danger' : 'warning'}`} role="status">
          <AlertTriangle size={18} />
          <div>
            <strong>
              {quotaExceeded
                ? `Limite diário atingido (${quotaUsed}/${quotaDaily})`
                : `${quotaPct}% do limite diário consumido (${quotaUsed}/${quotaDaily})`}
            </strong>
            <span>
              {quotaExceeded
                ? 'Novas chamadas retornarão HTTP 429 até a virada do dia (00:00 UTC-3).'
                : 'Considere upgrade para evitar interrupção quando atingir 100%.'}
            </span>
          </div>
          {!hasPlanAtLeast(currentPlan.slug, 'pro') && (
            <Link to="/app/billing" className="btn btn--primary btn--sm">Fazer upgrade</Link>
          )}
        </div>
      )}

      <div className="metrics-grid">
        <MetricCard label="Plano atual" value={currentPlan.nome} detail={currentPlan.limiteDiario} />
        <MetricCard label="API keys" value={hasApiKey ? '1 ativa' : '0 ativas'} detail={`limite: ${currentPlan.keyLimit}`} />
        <MetricCard
          label="Requisições hoje"
          value={quotaUsed !== null ? String(quotaUsed) : '—'}
          detail={
            quotaDaily
              ? `${quotaPct ?? 0}% de ${quotaDaily}`
              : quotaUsed !== null
                ? 'sem limite diário'
                : 'aguardando telemetria real'
          }
          loading={loadingUsage && hasApiKey}
        />
        <MetricCard
          label="Status da API"
          value={apiStatus === 'ok' ? 'Operacional' : 'Indisponível'}
          detail="ver /status"
          loading={apiStatus === 'loading'}
        />
      </div>

      <div className="action-grid">
        <Link to="/app/endpoints" className="action-card"><BookOpen size={22} /> <span>Endpoints</span><small>Consultar catálogo e testar rotas</small></Link>
        <Link to="/app/uso" className="action-card"><BarChart3 size={22} /> <span>Uso</span><small>Ver consumo da API</small></Link>
        <Link to="/app/api-keys" className="action-card"><KeyRound size={22} /> <span>API keys</span><small>Criar, testar e copiar chave</small></Link>
        <Link to="/app/datasets" className="action-card"><Database size={22} /> <span>Datasets</span><small>Ver escopo publicado</small></Link>
        <Link to="/app/billing" className="action-card"><CreditCard size={22} /> <span>Billing</span><small>Solicitar upgrade controlado</small></Link>
      </div>

      <div className="split-grid">
        {hasApiKey ? (
          <Card>
            <CardHeader title="Consumo recente" description="Dados reais aparecem aqui quando /me/uso retornar série de uso." />
            <UsageChart />
          </Card>
        ) : (
          <Card>
            <CardHeader title="Próxima ação" description="Crie ou informe uma API key para liberar testes e telemetria." />
            <div className="empty-state-inline">
              Sem API key ativa. O portal não mostra gráfico demo para evitar confusão comercial.
            </div>
            <Link to="/app/api-keys" className="btn btn--primary">Criar primeira API key</Link>
          </Card>
        )}
        <Card>
          <CardHeader title="Checklist de go-live" description="Itens críticos para vender com segurança." />
          <div className="status-list">
            <div className={`status-item status-item--${apiStatus}`}>
                {apiStatus === 'error' ? <AlertCircle size={16} /> : <Activity size={16} />}
                {apiStatus === 'loading' ? 'Verificando API…' : apiStatus === 'ok' ? 'API online' : 'API indisponível'}
              </div>
            <div><KeyRound /> API key obrigatória</div>
            <div><ShieldCheck /> Status honesto por dataset</div>
            <div><Database /> Parcial e roadmap separados do Core pronto</div>
          </div>
        </Card>
      </div>
    </div>
  );
}
