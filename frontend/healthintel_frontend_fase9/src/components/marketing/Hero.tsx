import { ArrowRight, Database, GitBranch, Gauge, FileText, ShieldCheck } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { ApiWidget } from './ApiWidget';

const HERO_SIGNALS: { Icon: LucideIcon; label: string }[] = [
  { Icon: Database, label: 'CADOP · SIB · CNES' },
  { Icon: GitBranch, label: 'Versionado /v1' },
  { Icon: Gauge, label: 'Rate limit por plano' },
  { Icon: FileText, label: 'Logs auditados' },
  { Icon: ShieldCheck, label: 'Sem enviar sua base' },
];

interface HeroProps {
  variant?: 'split' | 'centered';
  showWidget?: boolean;
}

export function Hero({ variant = 'split', showWidget = true }: HeroProps) {
  const isCentered = variant === 'centered';

  return (
    <section className="hero" data-variant={variant}>
      <div className="hero__grid-bg" aria-hidden="true"></div>
      <div className="hero__inner container">
        <div className={`hero__copy${isCentered ? ' hero__copy--center' : ''}`}>
          <span className="eyebrow">
            <span className="pulse-dot pulse-dot--mint"></span>
            HealthIntel Core ANS · Saúde Suplementar
          </span>
          <h1 className="hero__title">
            Dados ANS curados,{' '}
            <span className="hero__title-accent">
              versionados e prontos para consumo.
            </span>
          </h1>
          <p className="hero__sub">
            Reduza semanas de engenharia de dados em uma integração simples. Pare de manter
            robôs, layouts e cargas manuais da ANS dentro do seu time — consuma{' '}
            <code className="mono">CADOP</code>, <code className="mono">SIB</code>,{' '}
            <code className="mono">CNES</code> e derivados via API REST autenticada,
            versionada e auditável. Sem enviar sua base interna para terceiros.
          </p>
          <div className="hero__ctas">
            <a href="#planos" className="btn btn--primary btn--lg" title="Checkout via Stripe">
              Adquirir plano
              <ArrowRight size={16} />
            </a>
            <a href="#contato" className="btn btn--outline btn--lg">
              Falar com comercial
            </a>
          </div>
          <ul className="hero__signals">
            {HERO_SIGNALS.map((s) => (
              <li key={s.label}>
                <s.Icon size={13} />
                <span>{s.label}</span>
              </li>
            ))}
          </ul>
        </div>

        {!isCentered && showWidget && (
          <div className="hero__widget">
            <ApiWidget />
          </div>
        )}
      </div>

      {isCentered && showWidget && (
        <div className="container hero__widget-center">
          <ApiWidget compact />
        </div>
      )}
    </section>
  );
}
