import { useEffect, useState, Fragment } from 'react';
import { Globe, Key, Check } from 'lucide-react';

interface EndpointSample {
  method: 'GET';
  path: string;
  desc: string;
  response: Record<string, unknown>;
}

const ENDPOINT_SAMPLES: EndpointSample[] = [
  {
    method: 'GET',
    path: '/v1/operadoras',
    desc: 'Listagem paginada de operadoras',
    response: {
      data: [
        { registro_ans: '326305', razao_social: 'Hapvida Assistência Médica Ltda.', modalidade: 'Medicina de Grupo', uf_sede: 'CE', situacao: 'ATIVA', vidas: 8412903 },
        { registro_ans: '005711', razao_social: 'Bradesco Saúde S.A.', modalidade: 'Seguradora Especializada', uf_sede: 'RJ', situacao: 'ATIVA', vidas: 3621847 },
        { registro_ans: '359017', razao_social: 'Amil Assistência Médica Internacional', modalidade: 'Medicina de Grupo', uf_sede: 'SP', situacao: 'ATIVA', vidas: 3104221 },
      ],
      page: 1,
      per_page: 10,
      total: 743,
      competencia: '2025-09',
      fonte: 'ANS · Cadastro de Operadoras',
    },
  },
  {
    method: 'GET',
    path: '/v1/meta/datasets',
    desc: 'Catálogo de datasets e competências',
    response: {
      datasets: [
        { id: 'operadoras', versao: '1.4.0', competencia: '2025-09', registros: 743 },
        { id: 'beneficiarios', versao: '1.2.1', competencia: '2025-09', registros: 50847211 },
        { id: 'cnes_rede', versao: '1.1.0', competencia: '2025-08', registros: 351204 },
        { id: 'mercado_uf', versao: '1.0.3', competencia: '2025-09', registros: 27 },
        { id: 'rankings', versao: '1.0.2', competencia: '2025-09', registros: 743 },
      ],
      api_versao: 'v1',
      atualizado_em: '2025-10-14T03:00:00Z',
    },
  },
  {
    method: 'GET',
    path: '/v1/operadoras/326305',
    desc: 'Detalhe por registro ANS',
    response: {
      registro_ans: '326305',
      razao_social: 'Hapvida Assistência Médica Ltda.',
      cnpj: '63.554.067/0001-98',
      modalidade: 'Medicina de Grupo',
      uf_sede: 'CE',
      municipio_sede: 'Fortaleza',
      situacao: 'ATIVA',
      data_registro: '1993-06-14',
      vidas_total: 8412903,
      competencia: '2025-09',
      score_composto: 0.847,
    },
  },
  {
    method: 'GET',
    path: '/saude',
    desc: 'Health check do serviço',
    response: {
      status: 'ok',
      uptime_seconds: 4823917,
      versao: '1.4.0',
      regiao: 'sa-east-1',
    },
  },
];

function HighlightJson({ value, indent = 0 }: { value: unknown; indent?: number }) {
  const pad = '  '.repeat(indent);
  if (value === null) return <span className="jsx-null">null</span>;
  if (typeof value === 'boolean') return <span className="jsx-bool">{String(value)}</span>;
  if (typeof value === 'number') return <span className="jsx-num">{value}</span>;
  if (typeof value === 'string') return <span className="jsx-str">"{value}"</span>;
  if (Array.isArray(value)) {
    if (value.length === 0) return <>[]</>;
    return (
      <>
        [{'\n'}
        {value.map((v, i) => (
          <Fragment key={i}>
            {'  '.repeat(indent + 1)}
            <HighlightJson value={v} indent={indent + 1} />
            {i < value.length - 1 ? ',' : ''}
            {'\n'}
          </Fragment>
        ))}
        {pad}]
      </>
    );
  }
  if (typeof value === 'object' && value !== null) {
    const keys = Object.keys(value as Record<string, unknown>);
    if (keys.length === 0) return <>{'{}'}</>;
    return (
      <>
        {'{'}
        {'\n'}
        {keys.map((k, i) => (
          <Fragment key={k}>
            {'  '.repeat(indent + 1)}
            <span className="jsx-key">"{k}"</span>:{' '}
            <HighlightJson value={(value as Record<string, unknown>)[k]} indent={indent + 1} />
            {i < keys.length - 1 ? ',' : ''}
            {'\n'}
          </Fragment>
        ))}
        {pad}
        {'}'}
      </>
    );
  }
  return <>{String(value)}</>;
}

interface ApiWidgetProps {
  compact?: boolean;
}

export function ApiWidget({ compact = false }: ApiWidgetProps) {
  const [active, setActive] = useState(0);
  const [loading, setLoading] = useState(false);
  const [tick, setTick] = useState(0);
  const ep = ENDPOINT_SAMPLES[active];

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {
      setLoading(false);
      setTick((x) => x + 1);
    }, 380);
    return () => clearTimeout(t);
  }, [active]);

  const competencia = (ep.response as { competencia?: string }).competencia;

  return (
    <div className="api-widget">
      <div className="api-widget__chrome">
        <div className="api-widget__dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div className="api-widget__url">
          <Globe size={11} />
          <span className="mono">api.healthintel.com.br</span>
        </div>
        <div className="api-widget__live">
          <span className="pulse-dot"></span>
          <span>200 OK · {54 + (tick % 7) * 3}ms</span>
        </div>
      </div>

      <div className="api-widget__body">
        <div className="api-widget__list">
          <div className="api-widget__list-label">Endpoints</div>
          {ENDPOINT_SAMPLES.map((e, i) => (
            <button
              key={e.path}
              type="button"
              onClick={() => setActive(i)}
              className={`api-widget__ep${i === active ? ' is-active' : ''}`}
            >
              <span className="method-badge method-badge--get">{e.method}</span>
              <code className="api-widget__ep-path mono">{e.path}</code>
              {!compact && <span className="api-widget__ep-desc">{e.desc}</span>}
            </button>
          ))}
          <div className="api-widget__list-foot">
            <Key size={11} />
            <span className="mono">X-API-Key: hi_live_••••••a47f</span>
          </div>
        </div>

        <div className="api-widget__response">
          <div className="api-widget__resp-head">
            <div className="api-widget__resp-tabs">
              <span className="api-widget__resp-tab is-active">Response</span>
              <span className="api-widget__resp-tab">Headers</span>
              <span className="api-widget__resp-tab">cURL</span>
            </div>
            <span className="api-widget__resp-meta mono">application/json</span>
          </div>
          <pre className={`api-widget__code mono${loading ? ' is-loading' : ''}`}>
            <code>
              <HighlightJson value={ep.response} />
            </code>
          </pre>
          <div className="api-widget__resp-foot">
            <span>
              <Check size={12} />
              <span>200 · OK</span>
            </span>
            <span className="mono">competência {competencia || '—'}</span>
            <span className="mono">v1.4.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
