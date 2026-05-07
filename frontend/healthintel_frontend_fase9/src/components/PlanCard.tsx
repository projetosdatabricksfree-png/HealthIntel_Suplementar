import type { ApiPlan } from '../types/domain';
import { CheckCircle2 } from 'lucide-react';
import { ExternalLinkButton, LinkButton } from './Button';
import { cn } from '../utils/format';

export function PlanCard({ plan }: { plan: ApiPlan }) {
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
      {plan.stripePaymentLink ? (
        <ExternalLinkButton href={plan.stripePaymentLink} variant={plan.destaque ? 'primary' : 'secondary'}>
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
