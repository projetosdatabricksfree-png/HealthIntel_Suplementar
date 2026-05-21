import { Database, FileCheck2, GitBranch, Lock, ShieldCheck } from 'lucide-react';

const ITEMS = [
  {
    icon: FileCheck2,
    title: 'Fontes oficiais ANS',
    desc: 'CADOP, SIB, CNES, DIOPS, IDSS, NIP, Reajustes, Rol/TUSS — sem intermediário.',
  },
  {
    icon: GitBranch,
    title: 'API versionada /v1',
    desc: 'Quebras de contrato anunciadas via headers Sunset e Deprecation (6 meses).',
  },
  {
    icon: Database,
    title: 'Atualização D-1',
    desc: 'Ingestão automática após publicação da ANS · freshness por dataset.',
  },
  {
    icon: ShieldCheck,
    title: 'Auditoria por chave',
    desc: 'Logs de uso por API key, plano, endpoint, status e latência.',
  },
  {
    icon: Lock,
    title: 'LGPD-ready',
    desc: 'Apenas dados públicos ANS · sem PII · TISS/SIB individual sob solicitação.',
  },
];

export function TrustBar() {
  return (
    <section className="trust-bar" data-screen-label="trust">
      <div className="container">
        <p className="trust-bar__eyebrow">Por que confiar</p>
        <div className="trust-bar__grid">
          {ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.title} className="trust-bar__item">
                <span className="trust-bar__icon" aria-hidden="true">
                  <Icon size={16} />
                </span>
                <div>
                  <strong>{item.title}</strong>
                  <span>{item.desc}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
