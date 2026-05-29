import { useState } from 'react';
import { Check, Minus, Zap, ArrowRight, ArrowUpRight, Layers, Gauge, Info, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { commercialLinks } from '../../config/commercialLinks';
import type { PlanSlug } from '../../types/domain';

const NAME_TO_SLUG: Record<string, PlanSlug> = {
  FREE: 'free',
  STARTER: 'starter',
  PRO: 'pro',
  MAX: 'max',
};

interface PricingProps {
  currentSlug?: PlanSlug;
  onManageSubscription?: () => void;
}

type Ciclo = 'mensal' | 'anual';

interface Plan {
  name: string;
  tagline: string;
  priceMensal: string;
  priceAnual: string;
  cadenceMensal: string;
  cadenceAnual: string;
  economiaAnual?: string;
  limit: string;
  features: string[];
  limits: string[];
  kind: 'free' | 'buy' | 'contact';
  cta: string;
  href: string;
  hrefAnual?: string;
  recommended?: boolean;
  badge?: string;
  rateDetail: string;
}

const PLANS: Plan[] = [
  {
    name: 'FREE',
    tagline: 'Para testar a API sem cartão.',
    priceMensal: 'R$ 0',
    priceAnual: 'R$ 0',
    cadenceMensal: '/sempre',
    cadenceAnual: '/sempre',
    limit: '100 req/mês',
    badge: '14 dias de trial PRO',
    features: [
      '14 dias de trial PRO (2.500 req/dia)',
      'Após trial: 100 req/mês',
      '1 API key · ambiente sandbox',
      'Login com Google',
    ],
    limits: ['Sem suporte dedicado', 'Sem SLA'],
    kind: 'free',
    cta: 'Começar grátis',
    href: commercialLinks.login,
    rateDetail:
      'Trial PRO ativo nos primeiros 14 dias após cadastro (2.500 req/dia). Após o trial, 100 requisições/mês até o dia 1 do mês seguinte.',
  },
  {
    name: 'STARTER',
    tagline: 'Validação técnica e integração inicial.',
    priceMensal: 'R$ 99,99',
    priceAnual: 'R$ 999,90',
    cadenceMensal: '/mês',
    cadenceAnual: '/ano',
    economiaAnual: 'ganhe 2 meses',
    limit: '500 req/dia',
    features: [
      'Todos os datasets disponíveis',
      '3 API keys dedicadas',
      'Logs auditáveis na área do cliente',
      'Atualização por competência',
      'Swagger e Postman',
    ],
    limits: ['Sem SLA contratual'],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.starter,
    hrefAnual: commercialLinks.stripe.starterAnual,
    rateDetail: '500 req/dia · sem cap mensal · burst limitado. Excedente devolve HTTP 429 até virar o dia (00:00 UTC-3).',
  },
  {
    name: 'PRO',
    tagline: 'Times de BI, dados e produto em produção.',
    priceMensal: 'R$ 499',
    priceAnual: 'R$ 4.990',
    cadenceMensal: '/mês',
    cadenceAnual: '/ano',
    economiaAnual: 'ganhe 2 meses',
    limit: '2.500 req/dia',
    features: [
      'Todos os datasets + derivados',
      '10 API keys (live + sandbox)',
      'Equipe com até 3 usuários',
      'Logs exportáveis (CSV/JSON)',
      'Suporte assíncrono prioritário',
    ],
    limits: [],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.pro,
    hrefAnual: commercialLinks.stripe.proAnual,
    recommended: true,
    rateDetail: '2.500 req/dia · adequado para BI corporativo e produtos digitais. Rate limit elevado para bronze/prata.',
  },
  {
    name: 'MAX',
    tagline: 'Healthtechs e operadoras com alto volume.',
    priceMensal: 'R$ 1.499',
    priceAnual: 'R$ 14.990',
    cadenceMensal: '/mês',
    cadenceAnual: '/ano',
    economiaAnual: 'ganhe 2 meses',
    limit: '25.000 req/dia',
    features: [
      'Todos os datasets + Score composto',
      '25 API keys · múltiplos ambientes',
      'Equipe com até 10 usuários',
      'Webhooks de uso',
      'Suporte com SLA de resposta',
    ],
    limits: [],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.max,
    hrefAnual: commercialLinks.stripe.maxAnual,
    rateDetail: '25.000 req/dia · ~1 req cada 3,5s sustentado. Ideal para dashboards corporativos e ingestão batch.',
  },
];

function PlanCTA({
  plan,
  isCurrent,
  ciclo,
  onManageSubscription,
}: {
  plan: Plan;
  isCurrent?: boolean;
  ciclo: Ciclo;
  onManageSubscription?: () => void;
}) {
  const isBuy = plan.kind === 'buy';
  const isFree = plan.kind === 'free';
  const stripeUnconfigured = isBuy && !plan.href;
  const btnClass = `btn btn--lg pricing-card__cta ${plan.recommended ? 'btn--primary' : 'btn--outline'}`;

  if (isCurrent) {
    if (isFree) {
      return (
        <button type="button" className="btn btn--lg btn--outline pricing-card__cta" disabled aria-disabled="true">
          Plano atual
        </button>
      );
    }
    return (
      <button type="button" className="btn btn--lg btn--primary pricing-card__cta" onClick={onManageSubscription}>
        <span>Gerenciar assinatura</span>
        <ArrowUpRight size={14} />
      </button>
    );
  }

  if (stripeUnconfigured) {
    return (
      <Link to="/contato" className={btnClass}>
        <span>Falar com comercial</span>
        <ArrowRight size={14} />
      </Link>
    );
  }
  if (isFree) {
    return (
      <Link to={plan.href} className={btnClass}>
        <span>{plan.cta}</span>
        <ArrowRight size={14} />
      </Link>
    );
  }
  if (isBuy) {
    // Payment Links sao amarrados a um preco fixo: o anual tem URL propria.
    // Sem link anual configurado, cai no mensal em vez de mostrar preco errado.
    const href = ciclo === 'anual' ? (plan.hrefAnual || plan.href) : plan.href;
    return (
      <a href={href} className={btnClass} title={`Checkout via Stripe — cobrança ${ciclo}`}>
        <Zap size={14} />
        <span>{plan.cta}</span>
        <ArrowUpRight size={14} />
      </a>
    );
  }
  return (
    <Link to={plan.href} className={btnClass}>
      <span>{plan.cta}</span>
      <ArrowRight size={14} />
    </Link>
  );
}

export function Pricing({ currentSlug, onManageSubscription }: PricingProps = {}) {
  const [ciclo, setCiclo] = useState<Ciclo>('mensal');

  return (
    <>
      <div className="pricing-toggle" role="tablist" aria-label="Ciclo de cobrança">
        <button
          type="button"
          role="tab"
          aria-selected={ciclo === 'mensal'}
          className={`pricing-toggle__btn${ciclo === 'mensal' ? ' pricing-toggle__btn--active' : ''}`}
          onClick={() => setCiclo('mensal')}
        >
          Mensal
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={ciclo === 'anual'}
          className={`pricing-toggle__btn${ciclo === 'anual' ? ' pricing-toggle__btn--active' : ''}`}
          onClick={() => setCiclo('anual')}
        >
          Anual
          <span className="pricing-toggle__badge">
            <Sparkles size={11} /> Ganhe 2 meses
          </span>
        </button>
      </div>

      <div className="pricing-grid pricing-grid--4">
        {PLANS.map((p) => {
          const isCurrent = currentSlug ? NAME_TO_SLUG[p.name] === currentSlug : false;
          const price = ciclo === 'anual' ? p.priceAnual : p.priceMensal;
          const cadence = ciclo === 'anual' ? p.cadenceAnual : p.cadenceMensal;
          const economia = ciclo === 'anual' ? p.economiaAnual : undefined;
          return (
            <article
              key={p.name}
              className={`pricing-card${p.recommended ? ' pricing-card--rec' : ''}${p.kind === 'free' ? ' pricing-card--free' : ''}${isCurrent ? ' pricing-card--current' : ''}`}
            >
              {isCurrent && <span className="pricing-card__rec pricing-card__rec--current">Plano atual</span>}
              {!isCurrent && p.recommended && <span className="pricing-card__rec">Mais escolhido</span>}
              {!isCurrent && !p.recommended && p.badge && (
                <span className="pricing-card__rec pricing-card__rec--trial">
                  <Sparkles size={11} /> {p.badge}
                </span>
              )}
              <header className="pricing-card__head">
                <h3 className="pricing-card__name">{p.name}</h3>
                <p className="pricing-card__tagline">{p.tagline}</p>
              </header>
              <div className="pricing-card__price">
                <span className="pricing-card__amount">{price}</span>
                {cadence && <span className="pricing-card__cadence">{cadence}</span>}
              </div>
              {economia && (
                <p className="pricing-card__economia mono">{economia}</p>
              )}
              <div className="pricing-card__limit mono" title={p.rateDetail}>
                <Gauge size={12} />
                <span>{p.limit}</span>
                <Info size={11} className="pricing-card__limit-info" aria-label="Detalhes do rate limit" />
              </div>
              <PlanCTA plan={p} isCurrent={isCurrent} ciclo={ciclo} onManageSubscription={onManageSubscription} />
              <p className="pricing-card__cta-meta mono">
                {p.kind === 'buy'
                  ? (p.href ? `Checkout via Stripe · cobrança ${ciclo}` : 'Entre em contato para contratar')
                  : p.kind === 'free'
                  ? 'Sem cartão · login com Google'
                  : 'Resposta comercial em 1 dia útil'}
              </p>
              <ul className="pricing-card__features">
                {p.features.map((f) => (
                  <li key={f}>
                    <Check size={14} className="pricing-card__check" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              {p.limits.length > 0 && (
                <ul className="pricing-card__limits">
                  {p.limits.map((l) => (
                    <li key={l}>
                      <Minus size={14} />
                      <span>{l}</span>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          );
        })}
      </div>

      <div className="pricing-enterprise">
        <div className="pricing-enterprise__copy">
          <span className="eyebrow eyebrow--muted">
            <Layers size={11} /> Enterprise · pay-as-you-go
          </span>
          <h3 className="pricing-enterprise__title">
            A partir de R$ 5.000/mês + R$ 50 por mil req acima de 500k
          </h3>
          <p className="pricing-enterprise__desc">
            Mínimo mensal cobre 500.000 requisições. Acima disso, paga apenas pelo consumo real.
            Sem cap diário, SLA dedicado, SSO/SAML, IP allowlist com CIDR e contrato customizado.
            Negociado off-checkout — não é adquirido via Stripe self-service.
          </p>
        </div>
        <div className="pricing-enterprise__actions">
          <Link to="/contato?plano=enterprise" className="btn btn--outline btn--lg">
            Falar com comercial
            <ArrowRight size={14} />
          </Link>
          <span className="mono pricing-enterprise__meta">Resposta em até 1 dia útil</span>
        </div>
      </div>
    </>
  );
}
