import { Check, Minus, Zap, ArrowRight, ArrowUpRight, Layers, Gauge, Info } from 'lucide-react';
import { Link } from 'react-router-dom';
import { commercialLinks } from '../../config/commercialLinks';

interface Plan {
  name: string;
  tagline: string;
  price: string;
  cadence: string;
  limit: string;
  features: string[];
  limits: string[];
  kind: 'free' | 'buy' | 'contact';
  cta: string;
  href: string;
  recommended?: boolean;
  rateDetail: string;
}

const PLANS: Plan[] = [
  {
    name: 'FREE',
    tagline: 'Para testar a API sem cartão.',
    price: 'R$ 0',
    cadence: '/sempre',
    limit: '100 req/dia',
    features: [
      'Endpoints Core (somente leitura)',
      '1 API key · ambiente sandbox',
      'Latência best-effort',
      'Login com Google',
    ],
    limits: ['Sem suporte dedicado', 'Sem SLA'],
    kind: 'free',
    cta: 'Começar grátis',
    href: commercialLinks.login,
    rateDetail: '100 req/dia · ~1 req/seg · sem burst. Excedente devolve HTTP 429 até virar o dia (00:00 UTC-3).',
  },
  {
    name: 'STARTER',
    tagline: 'Validação técnica e integração inicial.',
    price: 'R$ 99,99',
    cadence: '/mês',
    limit: '30.000 req/dia',
    features: [
      'Todos os datasets disponíveis',
      '1 API key dedicada',
      'Logs auditáveis na área do cliente',
      'Atualização por competência',
      'Swagger e Postman',
    ],
    limits: ['Sem SLA contratual'],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.starter,
    rateDetail: '30k req/dia · ~5 req/seg sustentado · burst 10 req/seg em janelas curtas.',
  },
  {
    name: 'PRO',
    tagline: 'Times de BI, dados e produto em produção.',
    price: 'R$ 499',
    cadence: '/mês',
    limit: '150.000 req/dia',
    features: [
      'Todos os datasets + derivados',
      '3 API keys (live + sandbox)',
      'Rate limit elevado e burst',
      'Logs exportáveis (CSV/JSON)',
      'Suporte assíncrono prioritário',
    ],
    limits: [],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.pro,
    recommended: true,
    rateDetail: '150k req/dia · ~25 req/seg sustentado · burst 50 req/seg. Rate limit elevado para bronze/prata.',
  },
  {
    name: 'MAX',
    tagline: 'Healthtechs e operadoras com alto volume.',
    price: 'R$ 1.499',
    cadence: '/mês',
    limit: '500.000 req/dia',
    features: [
      'Todos os datasets + Score composto',
      '5 API keys · múltiplos ambientes',
      'Rate limit dedicado',
      'Alertas de uso e webhook de eventos',
      'Suporte com SLA de resposta',
    ],
    limits: [],
    kind: 'buy',
    cta: 'Adquirir plano',
    href: commercialLinks.stripe.max,
    rateDetail: '500k req/dia · ~100 req/seg sustentado · burst dedicado por chave. Ideal para ingestão batch noturna.',
  },
];

function PlanCTA({ plan }: { plan: Plan }) {
  const isBuy = plan.kind === 'buy';
  const isFree = plan.kind === 'free';
  const stripeUnconfigured = isBuy && !plan.href;
  const btnClass = `btn btn--lg pricing-card__cta ${plan.recommended ? 'btn--primary' : 'btn--outline'}`;

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
    return (
      <a href={plan.href} className={btnClass} title="Checkout via Stripe">
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

export function Pricing() {
  return (
    <>
      <div className="pricing-grid pricing-grid--4">
        {PLANS.map((p) => (
          <article
            key={p.name}
            className={`pricing-card${p.recommended ? ' pricing-card--rec' : ''}${p.kind === 'free' ? ' pricing-card--free' : ''}`}
          >
            {p.recommended && <span className="pricing-card__rec">Mais escolhido</span>}
            <header className="pricing-card__head">
              <h3 className="pricing-card__name">{p.name}</h3>
              <p className="pricing-card__tagline">{p.tagline}</p>
            </header>
            <div className="pricing-card__price">
              <span className="pricing-card__amount">{p.price}</span>
              {p.cadence && <span className="pricing-card__cadence">{p.cadence}</span>}
            </div>
            <div className="pricing-card__limit mono" title={p.rateDetail}>
              <Gauge size={12} />
              <span>{p.limit}</span>
              <Info size={11} className="pricing-card__limit-info" aria-label="Detalhes do rate limit" />
            </div>
            <PlanCTA plan={p} />
            <p className="pricing-card__cta-meta mono">
              {p.kind === 'buy'
                ? (p.href ? 'Checkout via Stripe · cartão ou Pix' : 'Entre em contato para contratar')
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
        ))}
      </div>

      <div className="pricing-enterprise">
        <div className="pricing-enterprise__copy">
          <span className="eyebrow eyebrow--muted">
            <Layers size={11} /> Enterprise · sem limites
          </span>
          <h3 className="pricing-enterprise__title">
            Volume ilimitado, SLA dedicado e contrato customizado
          </h3>
          <p className="pricing-enterprise__desc">
            Para operadoras, healthtechs e consultorias com alto volume diário, múltiplos
            ambientes, integração customizada e SLA contratual. Negociado sob contrato —
            não é adquirido via checkout.
          </p>
        </div>
        <div className="pricing-enterprise__actions">
          <Link to="/contato" className="btn btn--outline btn--lg">
            Falar com comercial
            <ArrowRight size={14} />
          </Link>
          <span className="mono pricing-enterprise__meta">Resposta em até 1 dia útil</span>
        </div>
      </div>
    </>
  );
}
