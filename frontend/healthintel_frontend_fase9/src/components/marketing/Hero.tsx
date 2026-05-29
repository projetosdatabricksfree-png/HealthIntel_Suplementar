import { ArrowRight, Database, GitBranch, Gauge, FileText, ShieldCheck } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { DataCatalogHero } from './DataCatalog';

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
            Catálogo de dados ANS · API REST versionada
          </span>
          <h1 className="hero__title">
            O catálogo de dados da ANS,{' '}
            <span className="hero__title-accent">
              curado, datado por competência e servido via API.
            </span>
          </h1>
          <p className="hero__sub">
            Não é mais um SaaS para você operar — é a base de dados da saúde suplementar como
            serviço. Consulte <code className="mono">CADOP</code>, <code className="mono">SIB</code>,{' '}
            <code className="mono">CNES</code>, DIOPS, IDSS e derivados como datasets versionados,
            cada registro carimbado por competência, sempre no envelope{' '}
            <code className="mono">{'{ dados, meta }'}</code>.
          </p>
          <div className="hero__ctas">
            <a href="#datasets" className="btn btn--primary btn--lg" title="Ver o catálogo de datasets">
              Explorar o catálogo
              <ArrowRight size={16} />
            </a>
            <a href="#planos" className="btn btn--outline btn--lg">
              Ver planos de acesso
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
            <DataCatalogHero />
          </div>
        )}
      </div>

      {isCentered && showWidget && (
        <div className="container hero__widget-center">
          <DataCatalogHero />
        </div>
      )}
    </section>
  );
}
