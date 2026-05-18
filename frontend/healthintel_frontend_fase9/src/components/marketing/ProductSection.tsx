import { Zap, Database, ShieldCheck, Gauge } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface Pillar {
  Icon: LucideIcon;
  badge: string;
  title: string;
  desc: string;
  proof: string;
}

const PILLARS: Pillar[] = [
  {
    Icon: Zap,
    badge: '5 min',
    title: 'Do checkout ao primeiro request',
    desc: 'Adquira o plano via Stripe, entre com Google e a API key aparece na sua área. Sem ticket, sem onboarding obrigatório.',
    proof: 'Suporte a cartão e Pix',
  },
  {
    Icon: Database,
    badge: 'Pipeline 24/7',
    title: 'Você não mantém ETL da ANS',
    desc: 'CADOP, SIB, CNES, DIOPS e derivados ingeridos, validados e versionados do nosso lado. Quando a ANS muda layout, nós ajustamos.',
    proof: 'Contratos /v1 com janela de deprecação',
  },
  {
    Icon: ShieldCheck,
    badge: 'LGPD-safe',
    title: 'Cruze ANS sem expor sua base interna',
    desc: 'Dados públicos curados, audit log por chave. Você não envia sua base privada para consultoria nenhuma.',
    proof: 'Logs exportáveis · API key por ambiente',
  },
  {
    Icon: Gauge,
    badge: 'Previsível',
    title: 'Pague por requisição, não por consultoria',
    desc: 'Planos transparentes em R$, com limite diário claro. Upgrade self-service quando o uso crescer.',
    proof: 'Sem cobrança por hora · sem surpresa',
  },
];

export function ProductSection() {
  return (
    <div className="pillars">
      {PILLARS.map((p) => (
        <article key={p.title} className="pillar">
          <header className="pillar__head">
            <span className="pillar__icon">
              <p.Icon size={18} />
            </span>
            <span className="pillar__badge mono">{p.badge}</span>
          </header>
          <h3 className="pillar__title">{p.title}</h3>
          <p className="pillar__desc">{p.desc}</p>
          <p className="pillar__proof mono">{p.proof}</p>
        </article>
      ))}
    </div>
  );
}
