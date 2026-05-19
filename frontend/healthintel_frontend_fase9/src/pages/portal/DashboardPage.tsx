import { Link } from 'react-router-dom';
import { Activity, BarChart3, BookOpen, CreditCard, Database, KeyRound, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { UsageChart } from '../../components/charts/UsageChart';
import { useAuth } from '../../hooks/useAuth';
import { coreEndpoints } from '../../data/endpoints';
import { datasetStats } from '../../data/datasets';

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h1>Bem-vindo, {user?.nome}</h1>
          <p>Visão operacional do seu consumo e acesso à API HealthIntel Core ANS.</p>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Plano atual" value={user?.plano || 'Free'} detail="Rate limit conforme contrato" />
        <MetricCard label="Endpoints Core" value={String(coreEndpoints.length)} detail="disponíveis e parciais" />
        <MetricCard label="Tabelas prontas" value={String(datasetStats.readyTables)} detail="vendáveis hoje" />
        <MetricCard label="Tabelas Premium" value={String(datasetStats.premiumTables)} detail="MDM e qualidade" />
      </div>

      <div className="action-grid">
        <Link to="/app/endpoints" className="action-card"><BookOpen size={22} /> <span>Endpoints</span><small>Consultar catálogo e testar rotas</small></Link>
        <Link to="/app/uso" className="action-card"><BarChart3 size={22} /> <span>Uso</span><small>Ver consumo demonstrativo</small></Link>
        <Link to="/app/api-keys" className="action-card"><KeyRound size={22} /> <span>API keys</span><small>Salvar, testar e copiar chave</small></Link>
        <Link to="/app/datasets" className="action-card"><Database size={22} /> <span>Datasets</span><small>Ver escopo publicado</small></Link>
        <Link to="/app/billing" className="action-card"><CreditCard size={22} /> <span>Billing</span><small>Solicitar upgrade controlado</small></Link>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Consumo recente" description="Requisições por dia, com fallback demo." />
          <UsageChart />
        </Card>
        <Card>
          <CardHeader title="Checklist de go-live" description="Itens críticos para vender com segurança." />
          <div className="status-list">
            <div><Activity /> API online</div>
            <div><KeyRound /> API key obrigatória</div>
            <div><ShieldCheck /> Status honesto por dataset</div>
            <div><Database /> Parcial e roadmap separados do Core pronto</div>
          </div>
        </Card>
      </div>
    </div>
  );
}
