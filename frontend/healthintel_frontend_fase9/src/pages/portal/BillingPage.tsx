import { Card, CardHeader, MetricCard } from '../../components/Card';
import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';

export function BillingPage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Billing</p>
          <h1>Plano e faturamento</h1>
          <p>Base visual para cobrança por plano, limite e consumo.</p>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Plano" value="Core API" detail="ativo" />
        <MetricCard label="Valor base" value="R$ 4.900" detail="mensal" />
        <MetricCard label="Consumo" value="6.430" detail="requisições" />
        <MetricCard label="Próximo ciclo" value="30/05" detail="demonstração" />
      </div>

      <Card>
        <CardHeader title="Planos disponíveis" description="O upgrade deve acionar `/admin/billing/upgrade` em fluxo administrativo." />
        <div className="plans-grid plans-grid-four">
          {plans.map((plan) => <PlanCard key={plan.nome} plan={plan} />)}
        </div>
      </Card>
    </div>
  );
}
