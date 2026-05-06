import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';

export function PricingPage() {
  return (
    <section className="page section">
      <div className="section-heading">
        <p className="eyebrow">Preços</p>
        <h1>Planos comerciais para iniciar venda</h1>
        <p>
          Estrutura inicial com piloto pago, plano API recorrente, BI/consultoria e enterprise sob contrato.
        </p>
      </div>
      <div className="plans-grid plans-grid-four">
        {plans.map((plan) => <PlanCard key={plan.nome} plan={plan} />)}
      </div>
    </section>
  );
}
