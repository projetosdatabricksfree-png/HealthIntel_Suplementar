import { datasets } from '../../data/datasets';

/* Métricas do catálogo, computadas do mesmo data/datasets.ts que alimenta as Docs. */
const totalDatasets = datasets.length;
const totalDominios = new Set(datasets.map((d) => d.dominio)).size;
const totalRegistros = datasets.reduce(
  (acc, d) => acc + (parseInt(d.linhas.replace(/\./g, ''), 10) || 0),
  0,
);

function compactInt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(0)}M+`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k+`;
  return String(n);
}

const STATS = [
  { value: String(totalDatasets), label: 'Datasets no catálogo', sub: 'consumo_ans + premium · versionados' },
  { value: String(totalDominios), label: 'Domínios cobertos', sub: 'operadoras · financeiro · rede · regulatório…' },
  { value: compactInt(totalRegistros), label: 'Registros servidos', sub: 'linhas entregues via /v1' },
  { value: '/v1', label: 'Contrato estável', sub: 'deprecação anunciada (Sunset)' },
];

export function StatsStrip() {
  return (
    <section className="stats" data-screen-label="stats">
      <div className="container">
        <div className="stats__grid">
          {STATS.map((s) => (
            <div key={s.label} className="stat">
              <div className="stat__value">{s.value}</div>
              <div className="stat__label">{s.label}</div>
              <div className="stat__sub">{s.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
