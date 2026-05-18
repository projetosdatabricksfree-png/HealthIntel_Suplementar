import { Check, Key, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const COVERAGE_DEFAULT = [
  'CADOP — Cadastro completo de Operadoras de saúde suplementar',
  'SIB — Beneficiários agregados por operadora, município e competência',
  'CNES — Rede de estabelecimentos, equipes e vínculos',
  'DIOPS / FIP — Demonstrações financeiras das operadoras',
  'IDSS — Índice de Desempenho da Saúde Suplementar',
  'NIP — Notificações de Intermediação Preliminar',
  'Reajustes — Histórico autorizado por operadora',
  'Rol de Procedimentos / TUSS — Catálogo de procedimentos',
  'Garantias Financeiras — Suficiência patrimonial',
  'Mercado, Rankings e Score — Derivados HealthIntel',
  'Metadados versionados (catálogo, competências, schemas)',
];

const COVERAGE_REQUEST = [
  'TISS — Tabela de Troca de Informação em Saúde Suplementar',
  'SIB nível beneficiário individual (identificável)',
  'Layouts ANS antigos descontinuados (sob análise técnica)',
  'Cargas customizadas com janela de competência específica',
];

export function Coverage() {
  return (
    <div className="coverage">
      <div className="coverage__col coverage__col--in">
        <div className="coverage__col-head">
          <span className="coverage__col-pill coverage__col-pill--ok">
            <Check size={12} /> Liberado por padrão
          </span>
          <p className="coverage__col-title">
            Cobrimos todas as tabelas publicadas pela ANS
          </p>
          <p className="coverage__col-sub">
            Pipeline gerenciado: ingestão, padronização, versionamento e exposição via API.
          </p>
        </div>
        <ul>
          {COVERAGE_DEFAULT.map((item, i) => (
            <li key={i}>
              <span className="coverage__bullet coverage__bullet--ok">
                <Check size={12} />
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
            <li key={i}>
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
