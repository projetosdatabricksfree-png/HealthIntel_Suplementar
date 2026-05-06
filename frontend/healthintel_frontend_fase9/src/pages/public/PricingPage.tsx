import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';

export function PricingPage() {
  return (
    <section className="page section">
      <div className="section-heading">
        <p className="eyebrow">Preços</p>
        <h1>Planos comerciais para operar com dados ANS</h1>
        <p>
          Valide a integração no Sandbox Técnico, avance para o Core API e amplie com suporte especializado sob contrato.
        </p>
      </div>
      <div className="plans-grid plans-grid-five">
        {plans.map((plan) => <PlanCard key={plan.nome} plan={plan} />)}
      </div>
    </section>
  );
}
