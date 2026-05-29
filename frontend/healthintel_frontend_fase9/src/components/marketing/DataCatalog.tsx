import { useEffect, useMemo, useState } from 'react';
import { Database, Layers, ArrowUpRight, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { datasets } from '../../data/datasets';
import type { DatasetStatus as DatasetRow, DeliveryStatus } from '../../types/domain';

/* Catálogo de dados — lê o mesmo catálogo real que alimenta as Docs (data/datasets.ts).
   O dado é o herói: dataset · domínio · grão · competência · registros · status · endpoint. */

const STATUS_SHORT: Record<DeliveryStatus, string> = {
  pronto: 'Pronto',
  parcial: 'Parcial',
  premium: 'Premium',
  roadmap: 'Roadmap',
  sem_dados: 'Roadmap',
};

const SERVED: DeliveryStatus[] = ['pronto', 'parcial', 'premium'];
const SERVED_ORDER: Record<DeliveryStatus, number> = {
  pronto: 0,
  premium: 1,
  parcial: 2,
  roadmap: 3,
  sem_dados: 4,
};

// Datasets em destaque no painel do hero — prontos, com números expressivos.
const HERO_CODES = [
  'operadora_360',
  'financeiro_operadora_trimestre',
  'score_operadora',
  'regulatorio_operadora',
  'idss',
  'tuss_vigente',
];

/** Extrai `/v1/...` (ou `/saude`) do campo `extracao`; null quando não há endpoint servido. */
function endpointPath(extracao: string): string | null {
  const m = extracao.match(/\/v1\/[A-Za-z0-9_\-{}/]*/);
  if (m) return m[0];
  return null;
}

/** Normaliza `janela` (ex.: '202603', '1T2023-4T2025', 'sem competencia') para exibição. */
function fmtComp(janela: string): string {
  const j = janela.trim();
  if (/nao publicado|pendente/i.test(j)) return '—';
  if (/sem competencia/i.test(j)) return 'vigente';
  const part = (p: string) => (/^\d{6}$/.test(p) ? `${p.slice(0, 4)}-${p.slice(4)}` : p);
  if (j.includes('-')) {
    const [a, b] = j.split('-');
    if (a && b) return `${part(a)}→${part(b)}`;
  }
  return part(j);
}

function StatusPill({ status }: { status: DeliveryStatus }) {
  return <span className={`status-pill status-pill--${status}`}>{STATUS_SHORT[status]}</span>;
}

/* ─── Hero: painel de catálogo "vivo" ─────────────────────────────────────── */
export function DataCatalogHero() {
  const rows = useMemo(
    () =>
      HERO_CODES.map((c) => datasets.find((d) => d.codigo === c)).filter(
        (d): d is DatasetRow => Boolean(d),
      ),
    [],
  );
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const [ms, setMs] = useState(54);

  useEffect(() => {
    if (paused) return;
    const id = setInterval(() => setActive((a) => (a + 1) % rows.length), 2600);
    return () => clearInterval(id);
  }, [paused, rows.length]);

  useEffect(() => {
    setMs(46 + Math.floor(Math.random() * 22));
  }, [active]);

  const ep = endpointPath(rows[active]?.extracao ?? '') ?? '/v1/operadoras';

  return (
    <div
      className="data-catalog data-catalog--hero"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="data-catalog__bar">
        <span className="data-catalog__bar-title">
          <Database size={13} /> Catálogo ANS
        </span>
        <span className="data-catalog__live mono">
          <span className="pulse-dot pulse-dot--mint" />
          {datasets.length} datasets · /v1
        </span>
      </div>

      <div className="data-catalog__grid">
        <div className="data-catalog__row data-catalog__row--head">
          <span>dataset</span>
          <span className="dc-col-comp">competência</span>
          <span className="dc-num">registros</span>
          <span className="dc-col-status">status</span>
        </div>
        {rows.map((d, i) => (
          <button
            key={d.codigo}
            type="button"
            className={`data-catalog__row${i === active ? ' is-active' : ''}`}
            onMouseEnter={() => setActive(i)}
            onFocus={() => setActive(i)}
            aria-label={`${d.nome} — ${d.linhas} registros, status ${STATUS_SHORT[d.status]}`}
          >
            <span className="dc-name">
              <strong>{d.nome}</strong>
              <code className="mono">{d.dominio}</code>
            </span>
            <span className="dc-col-comp mono">{fmtComp(d.janela)}</span>
            <span className="dc-num mono">{d.linhas}</span>
            <span className="dc-col-status">
              <StatusPill status={d.status} />
            </span>
          </button>
        ))}
      </div>

      <div className="data-catalog__foot mono">
        <span className="method-badge method-badge--get">GET</span>
        <span className="data-catalog__foot-path">{ep}</span>
        <span className="data-catalog__foot-status">
          <span className="pulse-dot pulse-dot--mint" />
          200 OK · {ms}ms
        </span>
      </div>
    </div>
  );
}

/* ─── Seção: catálogo completo (datasets servidos) ────────────────────────── */
const FILTROS: Array<{ key: 'todos' | DeliveryStatus; label: string }> = [
  { key: 'todos', label: 'Todos' },
  { key: 'pronto', label: 'Pronto' },
  { key: 'premium', label: 'Premium' },
  { key: 'parcial', label: 'Parcial' },
];

export function DataCatalog() {
  const served = useMemo(
    () =>
      datasets
        .filter((d) => SERVED.includes(d.status))
        .sort(
          (a, b) =>
            SERVED_ORDER[a.status] - SERVED_ORDER[b.status] ||
            a.dominio.localeCompare(b.dominio) ||
            a.nome.localeCompare(b.nome),
        ),
    [],
  );
  const [filtro, setFiltro] = useState<'todos' | DeliveryStatus>('todos');
  const rows = filtro === 'todos' ? served : served.filter((d) => d.status === filtro);

  const count = (k: 'todos' | DeliveryStatus) =>
    k === 'todos' ? served.length : served.filter((d) => d.status === k).length;

  return (
    <div className="data-catalog data-catalog--full">
      <div className="data-catalog__bar data-catalog__bar--full">
        <span className="data-catalog__bar-title">
          <Layers size={13} /> Catálogo · {served.length} datasets servidos
        </span>
        <div className="data-catalog__filters" role="tablist" aria-label="Filtrar por status">
          {FILTROS.map((f) => (
            <button
              key={f.key}
              type="button"
              role="tab"
              aria-selected={filtro === f.key}
              className={`chip${filtro === f.key ? ' chip-active' : ''}`}
              onClick={() => setFiltro(f.key)}
            >
              {f.label}
              <span className="chip-count">{count(f.key)}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="data-catalog__scroll">
        <table className="catalog-table">
          <thead>
            <tr>
              <th>dataset</th>
              <th>domínio</th>
              <th className="catalog-table__grao">grão</th>
              <th>competência</th>
              <th className="dc-num">registros</th>
              <th>endpoint</th>
              <th>status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => {
              const ep = endpointPath(d.extracao);
              return (
                <tr key={d.codigo}>
                  <td className="catalog-table__name">
                    <strong>{d.nome}</strong>
                    <small className="mono">{d.tabela}</small>
                  </td>
                  <td className="catalog-table__dom">{d.dominio}</td>
                  <td className="catalog-table__grao mono">{d.grao}</td>
                  <td className="mono catalog-table__comp">{fmtComp(d.janela)}</td>
                  <td className="dc-num mono">{d.linhas}</td>
                  <td>
                    {ep ? (
                      <span className="catalog-table__ep mono">
                        <span className="method-badge method-badge--get">GET</span> {ep}
                      </span>
                    ) : (
                      <span className="catalog-table__ep catalog-table__ep--none">sob recorte</span>
                    )}
                  </td>
                  <td>
                    <StatusPill status={d.status} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="data-catalog__legend">
        <span className="data-catalog__legend-note">
          Grão, janela de competência e registros lidos do catálogo de produção. Status real por
          dataset em <code>/status/cobertura</code>.
        </span>
        <span className="data-catalog__legend-links">
          <Link to="/documentacao" className="data-catalog__legend-link">
            Catálogo completo + cURL <ArrowUpRight size={13} />
          </Link>
          <a
            href="https://api.healthintel.com.br/v1/status/cobertura"
            target="_blank"
            rel="noreferrer"
            className="data-catalog__legend-link"
          >
            /status/cobertura <ExternalLink size={12} />
          </a>
        </span>
      </div>
    </div>
  );
}
