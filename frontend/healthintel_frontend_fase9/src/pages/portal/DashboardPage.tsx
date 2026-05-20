import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, AlertCircle, BarChart3, BookOpen, CreditCard, Database, KeyRound, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { UsageChart } from '../../components/charts/UsageChart';
import { useAuth } from '../../hooks/useAuth';
import { requestApi } from '../../services/apiClient';
import { getApiKey } from '../../services/storage';
import { getCurrentPlan, hasPlanAtLeast } from '../../data/planRules';

export function DashboardPage() {
  const { user } = useAuth();
  const [apiStatus, setApiStatus] = useState<'loading' | 'ok' | 'error'>('loading');
  const currentPlan = getCurrentPlan(user?.tenant_ativo?.plano_nome);
  const hasApiKey = Boolean(getApiKey().trim());
  useEffect(() => {
    requestApi('/saude', { apiKey: '' }).then((res) => setApiStatus(res.ok ? 'ok' : 'error'));
  }, []);

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

      <div className="metrics-grid">
        <MetricCard label="Plano atual" value={currentPlan.nome} detail={currentPlan.limiteDiario} />
        <MetricCard label="API keys" value={hasApiKey ? '1 ativa' : '0 ativas'} detail={`limite: ${currentPlan.keyLimit}`} />
        <MetricCard label="Requisições hoje" value="—" detail="aguardando telemetria real" />
        <MetricCard label="Status da API" value={apiStatus === 'ok' ? 'Operacional' : apiStatus === 'loading' ? 'Verificando' : 'Indisponível'} detail="ver /status" />
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
