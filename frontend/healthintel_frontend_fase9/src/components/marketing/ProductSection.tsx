import { Database, GitBranch, CalendarClock, ShieldCheck } from 'lucide-react';
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
    Icon: Database,
    badge: 'pipeline gerenciado',
    title: 'Você não mantém ETL da ANS',
    desc: 'Download, validação de layout, padronização e versionamento ficam do nosso lado. Quando a ANS muda o layout do arquivo, nós ajustamos — seu código não quebra.',
    proof: 'Ingestão D-1 · freshness por dataset',
  },
  {
    Icon: GitBranch,
    badge: 'contrato /v1',
    title: 'Envelope estável e versionado',
    desc: 'Toda resposta vem em { dados, meta }. Quebras de contrato disparam /v2 com 6 meses de deprecação anunciada nos headers Sunset e Deprecation.',
    proof: 'JSON consistente · sem surpresa de schema',
  },
  {
    Icon: CalendarClock,
    badge: 'datado',
    title: 'Cada registro tem competência',
    desc: 'Do trimestre DIOPS ao ano-base IDSS, toda linha carrega competência e janela. Leitura ponto-no-tempo, histórico auditável e backfill rastreável.',
    proof: 'YYYYMM · janela explícita por dataset',
  },
  {
    Icon: ShieldCheck,
    badge: 'LGPD-safe',
    title: 'Cruze ANS sem expor sua base',
    desc: 'Somente dados públicos da ANS, com audit log por chave. Você enriquece e cruza a regulação sem enviar sua base interna para consultoria nenhuma.',
    proof: 'Sem PII · log de uso por API key',
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
