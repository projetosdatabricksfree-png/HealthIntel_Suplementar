import { useMemo, useState, type ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, Crown, Calendar, Ban, Code2 } from 'lucide-react';
import { CopyButton } from '../../components/CopyButton';
import { datasets, statusLabel, statusTone } from '../../data/datasets';
import type { DeliveryStatus } from '../../types/domain';

const API_BASE = 'https://api.healthintel.com.br/v1';

const RATE_LIMITS = [
  { plano: 'FREE', rpm: '10', dia: '100 req/dia', preco: 'R$ 0' },
  { plano: 'STARTER', rpm: '120', dia: '30.000 req/dia', preco: 'R$ 99,99 / mês' },
  { plano: 'PRO', rpm: '300', dia: '150.000 req/dia', preco: 'R$ 499 / mês' },
  { plano: 'MAX', rpm: '1.000', dia: '500.000 req/dia', preco: 'R$ 1.499 / mês' },
  { plano: 'ENTERPRISE', rpm: '5.000+', dia: 'Contratual', preco: 'Sob contrato' },
];

const ERROS_COMUNS = [
  { codigo: '401', nome: 'Unauthorized', causa: 'Header `X-API-Key` ausente ou inválido.' },
  { codigo: '403', nome: 'Forbidden', causa: 'Plano não autoriza o endpoint ou camada solicitada.' },
  { codigo: '404', nome: 'Not Found', causa: 'Recurso (registro_ans, competência) não existe ou está fora da janela.' },
  { codigo: '422', nome: 'Unprocessable Content', causa: 'Parâmetros inválidos (ver `detail` na resposta).' },
  { codigo: '429', nome: 'Too Many Requests', causa: 'Rate limit por minuto ou limite diário excedido. Header `Retry-After`.' },
  { codigo: '500', nome: 'Server Error', causa: 'Erro inesperado — abrir ticket. Backend não loga stack trace em produção.' },
];

const statusIcone: Record<DeliveryStatus, ReactElement> = {
  pronto: <CheckCircle2 size={16} className="status-pronto" />,
  parcial: <AlertTriangle size={16} className="status-parcial" />,
  premium: <Crown size={16} className="status-premium" />,
  roadmap: <Calendar size={16} className="status-roadmap" />,
  sem_dados: <Ban size={16} className="status-sem-dados" />,
};

export function DocumentacaoPage() {
  const [filtroStatus, setFiltroStatus] = useState<'todos' | DeliveryStatus>('todos');
  const datasetsFiltrados = useMemo(
    () =>
      filtroStatus === 'todos'
        ? datasets
        : datasets.filter((d) => d.status === filtroStatus),
    [filtroStatus]
  );

  const porDominio = useMemo(() => {
    const m = new Map<string, typeof datasets>();
    for (const d of datasetsFiltrados) {
      const arr = m.get(d.dominio) || [];
      arr.push(d);
      m.set(d.dominio, arr);
    }
    return Array.from(m.entries()).sort((a, b) => a[0].localeCompare(b[0]));
  }, [datasetsFiltrados]);

  return (
    <div className="docs-page">
      <header className="docs-hero">
        <div className="container">
          <p className="eyebrow">Documentação técnica</p>
          <h1>API HealthIntel — Dados ANS prontos para integração</h1>
          <p className="docs-hero__sub">
            Tudo que você precisa para autenticar, consumir e integrar a API: catálogo completo de
            datasets, exemplos cURL, rate limits, paginação e erros comuns.
          </p>
          <div className="docs-hero__cta">
            <Link to="/login?mode=cadastro" className="btn btn--primary">
              Criar conta grátis
            </Link>
            <a href="#quickstart" className="btn btn--ghost">
              Quickstart
            </a>
          </div>
        </div>
      </header>

      <div className="container docs-body">
        <nav className="docs-toc" aria-label="Sumário">
          <p className="docs-toc__title">Nesta página</p>
          <a href="#visao-geral">Visão geral</a>
          <a href="#quickstart">Quickstart cURL</a>
          <a href="#autenticacao">Autenticação</a>
          <a href="#base-url">Base URL e versionamento</a>
          <a href="#rate-limits">Rate limits por plano</a>
          <a href="#paginacao">Paginação</a>
          <a href="#erros">Erros comuns</a>
          <a href="#catalogo">Catálogo de datasets</a>
        </nav>

        <article className="docs-content">
          <section id="visao-geral">
            <h2>Visão geral</h2>
            <p>
              A API HealthIntel entrega dados públicos da ANS (CADOP, SIB, IDSS, IGR, NIP, DIOPS,
              CNES, TISS/TUSS) já curados, particionados e indexados para consumo via HTTPS. Nada
              de baixar ZIP, mexer em layout fixo ou descobrir o que mudou no PDF de Resolução.
              Tudo via JSON, com versionamento.
            </p>
            <p>
              Todos os endpoints retornam o envelope padrão{' '}
              <code>{`{ "dados": [...], "meta": {...} }`}</code> — onde{' '}
              <code>meta</code> traz <code>total</code>, <code>pagina</code>,{' '}
              <code>por_pagina</code> e <code>competencia_referencia</code> quando aplicável.
            </p>
          </section>

          <section id="quickstart">
            <h2>Quickstart cURL</h2>
            <p>
              Cole sua chave (header <code>X-API-Key</code>) e faça a primeira chamada em segundos.
            </p>
            <div className="docs-code-block">
              <pre className="docs-code">
                <code>{`curl -H "X-API-Key: hi_test_SUA_CHAVE" \\
  "${API_BASE}/operadoras?page=1&page_size=10"`}</code>
              </pre>
              <CopyButton
                value={`curl -H "X-API-Key: hi_test_SUA_CHAVE" "${API_BASE}/operadoras?page=1&page_size=10"`}
              />
            </div>
            <p>Resposta resumida:</p>
            <pre className="docs-code">
              <code>{`{
  "dados": [
    { "registro_ans": "000337", "razao_social": "...", "modalidade": "Cooperativa Médica" }
  ],
  "meta": {
    "total": 757,
    "pagina": 1,
    "por_pagina": 10,
    "competencia_referencia": "202603",
    "versao_dataset": "v3.0"
  }
}`}</code>
            </pre>
          </section>

          <section id="autenticacao">
            <h2>Autenticação</h2>
            <p>
              Toda requisição deve enviar o header <code>X-API-Key</code> com sua chave. As chaves
              têm prefixo público: <code>hi_test_*</code> (sandbox) ou <code>hi_live_*</code>{' '}
              (produção).
            </p>
            <p>
              Para criar a primeira chave: <Link to="/login?mode=cadastro">criar conta grátis</Link>{' '}
              → verificar e-mail → entrar no portal → <strong>API keys → Criar nova chave</strong>.
              A chave aparece <strong>uma única vez</strong>. Guarde imediatamente.
            </p>
            <p>
              Nunca exponha a chave em código client-side público (HTML, JS de browser) ou em
              repositórios versionados. Use variáveis de ambiente do servidor.
            </p>
          </section>

          <section id="base-url">
            <h2>Base URL e versionamento</h2>
            <p>
              Base URL única: <code>{API_BASE}</code>. Todos os endpoints começam com{' '}
              <code>/v1/</code>. Quebras de contrato disparam <code>/v2/</code> com janela de
              deprecação de 6 meses anunciada nos headers <code>Sunset</code> e <code>Deprecation</code>.
            </p>
          </section>

          <section id="rate-limits">
            <h2>Rate limits por plano</h2>
            <table className="docs-table">
              <thead>
                <tr>
                  <th>Plano</th>
                  <th>RPM (por minuto)</th>
                  <th>Quota diária</th>
                  <th>Preço</th>
                </tr>
              </thead>
              <tbody>
                {RATE_LIMITS.map((r) => (
                  <tr key={r.plano}>
                    <td>
                      <strong>{r.plano}</strong>
                    </td>
                    <td>{r.rpm}</td>
                    <td>{r.dia}</td>
                    <td>{r.preco}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="docs-note">
              Excedeu o limite? Retorna HTTP 429 com header <code>Retry-After</code>. Para upgrade
              em tempo real: <Link to="/precos">/precos</Link>.
            </p>
          </section>

          <section id="paginacao">
            <h2>Paginação</h2>
            <p>
              Endpoints de listagem aceitam <code>page</code> (1-based) e <code>page_size</code>{' '}
              (máx. 200). A resposta carrega <code>meta.total</code>, <code>meta.pagina</code> e{' '}
              <code>meta.por_pagina</code>.
            </p>
            <pre className="docs-code">
              <code>{`GET ${API_BASE}/operadoras?page=2&page_size=50`}</code>
            </pre>
          </section>

          <section id="erros">
            <h2>Erros comuns</h2>
            <table className="docs-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Nome</th>
                  <th>Causa</th>
                </tr>
              </thead>
              <tbody>
                {ERROS_COMUNS.map((e) => (
                  <tr key={e.codigo}>
                    <td>
                      <code>{e.codigo}</code>
                    </td>
                    <td>{e.nome}</td>
                    <td>{e.causa}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="docs-note">
              Todas as respostas de erro seguem{' '}
              <code>{`{ "detail": { "codigo": "...", "mensagem": "..." } }`}</code>.
            </p>
          </section>

          <section id="catalogo">
            <div className="docs-cat-head">
              <h2>Catálogo de datasets</h2>
              <div className="docs-cat-filter">
                <label htmlFor="filtro-status">Filtrar por status:</label>
                <select
                  id="filtro-status"
                  value={filtroStatus}
                  onChange={(e) => setFiltroStatus(e.target.value as 'todos' | DeliveryStatus)}
                >
                  <option value="todos">Todos ({datasets.length})</option>
                  {(['pronto', 'parcial', 'premium', 'roadmap', 'sem_dados'] as DeliveryStatus[]).map(
                    (s) => (
                      <option key={s} value={s}>
                        {statusLabel[s]} ({datasets.filter((d) => d.status === s).length})
                      </option>
                    )
                  )}
                </select>
              </div>
            </div>

            {porDominio.map(([dominio, lista]) => (
              <div key={dominio} className="docs-dominio">
                <h3>{dominio}</h3>
                <div className="docs-datasets">
                  {lista.map((d) => (
                    <article
                      key={d.codigo}
                      className={`docs-dataset docs-dataset--${statusTone[d.status]}`}
                    >
                      <header>
                        <div>
                          <span className="docs-dataset__status">
                            {statusIcone[d.status]} {statusLabel[d.status]}
                          </span>
                          <h4>{d.nome}</h4>
                          <p className="docs-dataset__desc">{d.descricao}</p>
                        </div>
                      </header>
                      <dl className="docs-dataset__props">
                        <div>
                          <dt>Endpoint</dt>
                          <dd>
                            <code>{d.extracao}</code>
                          </dd>
                        </div>
                        <div>
                          <dt>Atualização</dt>
                          <dd>{d.atualizacao}</dd>
                        </div>
                        <div>
                          <dt>Janela</dt>
                          <dd>{d.janela}</dd>
                        </div>
                        <div>
                          <dt>Grão</dt>
                          <dd>{d.grao}</dd>
                        </div>
                      </dl>
                      {d.status === 'pronto' && d.extracao.includes('/v1') && (() => {
                        const path = d.extracao.replace(/.*?\/v1/, '').split(' ')[0].replace('GET ', '');
                        const curl = `curl -H "X-API-Key: hi_test_…" ${API_BASE}${path}`;
                        return (
                          <div className="docs-code-block docs-code-block--inline">
                            <pre className="docs-code docs-code--inline">
                              <code>
                                <Code2 size={11} /> {curl}
                              </code>
                            </pre>
                            <CopyButton value={curl} />
                          </div>
                        );
                      })()}
                      <p className="docs-dataset__uso">
                        <strong>Uso comercial:</strong> {d.usoComercial}
                      </p>
                    </article>
                  ))}
                </div>
              </div>
            ))}
          </section>

          <footer className="docs-cta">
            <h3>Pronto pra integrar?</h3>
            <p>
              Crie uma conta gratuita, gere sua API key sandbox e comece a testar em menos de 1
              minuto.
            </p>
            <div className="button-row">
              <Link to="/login?mode=cadastro" className="btn btn--primary">
                Criar conta grátis
              </Link>
              <Link to="/precos" className="btn btn--ghost">
                Ver planos
              </Link>
              <Link to="/contato" className="btn btn--ghost">
                Falar com comercial
              </Link>
            </div>
          </footer>
        </article>
      </div>
    </div>
  );
}
