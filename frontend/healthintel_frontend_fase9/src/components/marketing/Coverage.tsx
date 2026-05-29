import { useEffect, useState } from 'react';
import { Check, Key, ArrowRight, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { buildUrl } from '../../services/apiClient';

type SituacaoCobertura = 'ok' | 'parcial' | 'vazio' | 'indisponivel';

interface DatasetCobertura {
  dataset: string;
  rotulo: string;
  descricao: string;
  tabela: string;
  min_competencia: string | null;
  max_competencia: string | null;
  linhas: number;
  situacao: SituacaoCobertura;
}

const COVERAGE_EM_PRODUCAO_FALLBACK = [
  'CADOP — Cadastro de Operadoras (a partir de 2024)',
  'DIOPS — Demonstrações financeiras das operadoras (3 anos completos)',
  'IDSS — Índice de Desempenho da Saúde Suplementar (13 anos)',
  'Rol de Procedimentos / TUSS — Catálogo de procedimentos vigentes',
  'Prudencial / Garantias Financeiras — Suficiência patrimonial (desde 2024)',
  'Mercado, Rankings e Score — Derivados HealthIntel',
  'SIB — Beneficiários por município e operadora (2025 em diante)',
  'Metadados versionados (catálogo, competências, schemas)',
];

const COVERAGE_BACKFILL_FALLBACK = [
  'SIB histórico (2023–2024)',
  'NIP — Notificações pós-2020',
  'Reajustes — histórico autorizado por operadora',
  'VDA — Valor a Devolver (componente de Garantias)',
  'Monitoramento de garantia de atendimento',
  'FIP — histórico completo',
  'CADOP — janela pré-2024',
  'CNES — granularidade por estabelecimento',
];

const COVERAGE_REQUEST = [
  'TISS — Tabela de Troca de Informação em Saúde Suplementar',
  'SIB nível beneficiário individual (identificável)',
  'Layouts ANS antigos descontinuados (sob análise técnica)',
  'Cargas customizadas com janela de competência específica',
];

function formatarRange(min: string | null, max: string | null): string {
  if (!min && !max) return '—';
  if (!min) return `até ${max}`;
  if (!max) return `desde ${min}`;
  if (min === max) return min;
  return `${min} → ${max}`;
}

function formatarDataset(d: DatasetCobertura): string {
  const range = formatarRange(d.min_competencia, d.max_competencia);
  if (range === '—') return `${d.rotulo} — ${d.descricao}`;
  return `${d.rotulo} — ${d.descricao} (${range})`;
}

export function Coverage() {
  const [datasets, setDatasets] = useState<DatasetCobertura[] | null>(null);
  const [erro, setErro] = useState<boolean>(false);

  useEffect(() => {
    let ativo = true;
    fetch(buildUrl('/status/cobertura'), { headers: { Accept: 'application/json' } })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then((json: { dados?: DatasetCobertura[] }) => {
        if (!ativo) return;
        if (Array.isArray(json?.dados) && json.dados.length > 0) {
          setDatasets(json.dados);
        } else {
          setErro(true);
        }
      })
      .catch(() => {
        if (ativo) setErro(true);
      });
    return () => {
      ativo = false;
    };
  }, []);

  const emProducao =
    datasets && !erro
      ? datasets.filter((d) => d.situacao === 'ok').map(formatarDataset)
      : COVERAGE_EM_PRODUCAO_FALLBACK;

  const backfill =
    datasets && !erro
      ? datasets
          .filter((d) => d.situacao === 'parcial' || d.situacao === 'vazio')
          .map((d) =>
            d.situacao === 'vazio'
              ? `${d.rotulo} — ${d.descricao} (sem dados ainda)`
              : formatarDataset(d),
          )
      : COVERAGE_BACKFILL_FALLBACK;

  return (
    <div className="coverage">
      <div className="coverage__col coverage__col--in">
        <div className="coverage__col-head">
          <span className="coverage__col-pill coverage__col-pill--ok">
            <Check size={12} /> Em produção hoje
          </span>
          <p className="coverage__col-title">
            Cobertura ANS — atualizada continuamente
          </p>
          <p className="coverage__col-sub">
            Pipeline gerenciado: ingestão, padronização, versionamento e exposição via API.
            Dados desta lista são lidos em tempo real do endpoint público{' '}
            <code>/status/cobertura</code>.
          </p>
        </div>
        <ul>
          {emProducao.map((item, i) => (
            <li key={`prod-${i}`}>
              <span className="coverage__bullet coverage__bullet--ok">
                <Check size={12} />
              </span>
              {item}
            </li>
          ))}
        </ul>

        <div className="coverage__col-head coverage__col-head--sub">
          <span className="coverage__col-pill coverage__col-pill--backfill">
            <Clock size={12} /> Backfill em andamento
          </span>
          <p className="coverage__col-sub">
            Datasets em ingestão histórica ativa ou aguardando reconciliação de layout.
            Liberados conforme cada lote conclui e passa nos testes de qualidade.
          </p>
        </div>
        <ul>
          {backfill.map((item, i) => (
            <li key={`bf-${i}`}>
              <span className="coverage__bullet coverage__bullet--backfill">
                <Clock size={12} />
              </span>
              {item}
            </li>
          ))}
        </ul>
      </div>
      <div className="coverage__col coverage__col--out">
        <div className="coverage__col-head">
          <span className="coverage__col-pill coverage__col-pill--request">
            <Key size={12} /> Sob solicitação
          </span>
          <p className="coverage__col-title">
            Tabelas sensíveis liberadas caso a caso
          </p>
          <p className="coverage__col-sub">
            TISS e SIB nível beneficiário exigem análise técnica e comercial antes da liberação.
          </p>
        </div>
        <ul>
          {COVERAGE_REQUEST.map((item, i) => (
            <li key={`req-${i}`}>
              <span className="coverage__bullet coverage__bullet--request">
                <Key size={12} />
              </span>
              {item}
            </li>
          ))}
        </ul>
        <Link to="/contato" className="coverage__cta">
          Solicitar tabela específica
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
