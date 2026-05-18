import type { ApiPlan } from '../types/domain';
import { CheckCircle2 } from 'lucide-react';
import { ExternalLinkButton, LinkButton } from './Button';
import { cn } from '../utils/format';
import { criarCheckoutSessao } from '../services/checkoutApi';
import { useNotification } from './NotificationProvider';

export function PlanCard({ plan }: { plan: ApiPlan }) {
  const { error } = useNotification();

  async function startCheckout() {
    if (!plan.checkoutSlug) return;
    try {
      const checkoutUrl = await criarCheckoutSessao(plan.checkoutSlug);
      window.location.href = checkoutUrl;
    } catch (err) {
      error(err instanceof Error ? err.message : 'Falha ao iniciar pagamento.');
    }
  }

  return (
    <article className={cn('plan-card', plan.destaque && 'plan-card-featured')}>
      {plan.destaque && <span className="plan-ribbon">Recomendado</span>}
      <h3>{plan.nome}</h3>
      <strong>{plan.preco}</strong>
      <p>{plan.descricao}</p>
      <div className="plan-list">
        {plan.features.map((item) => (
          <div key={item}><CheckCircle2 size={18} /> <span>{item}</span></div>
        ))}
      </div>
      <div className="plan-limits">
        {plan.limits.map((item) => <small key={item}>{item}</small>)}
      </div>
      {plan.checkoutSlug ? (
        <button
          type="button"
          className={cn('btn', plan.destaque ? 'btn-primary' : 'btn-secondary')}
          onClick={startCheckout}
        >
          Contratar agora
        </button>
      ) : plan.stripePaymentLink ? (
        <ExternalLinkButton
          href={plan.stripePaymentLink}
          variant={plan.destaque ? 'primary' : 'secondary'}
        >
          Contratar agora
        </ExternalLinkButton>
      ) : (
        <LinkButton
          to={`/contato?plano=${encodeURIComponent(plan.slug)}`}
          variant={plan.destaque ? 'primary' : 'secondary'}
        >
          Solicitar acesso
        </LinkButton>
      )}
    </article>
  );
}
