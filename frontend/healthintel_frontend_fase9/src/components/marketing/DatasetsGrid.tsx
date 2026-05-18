import {
  Building2,
  Users,
  Hospital,
  Map,
  TrendingUp,
  Gauge,
  AlertTriangle,
  BookOpen,
  Shield,
  Landmark,
  Sparkles,
  Key,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

type DatasetStatus = 'disponivel' | 'solicitacao';

interface Dataset {
  Icon: LucideIcon;
  name: string;
  desc: string;
  source: string;
  status: DatasetStatus;
}

const DATASETS: Dataset[] = [
  { Icon: Building2, name: 'CADOP', desc: 'Cadastro de Operadoras: modalidade, situação, UF e registro ANS.', source: 'ANS · Cadastro de Operadoras', status: 'disponivel' },
  { Icon: Users, name: 'SIB', desc: 'Beneficiários agregados por operadora, município e competência.', source: 'ANS · SIB agregado', status: 'disponivel' },
  { Icon: Hospital, name: 'CNES', desc: 'Rede de estabelecimentos por município e UF, com vínculos.', source: 'DataSUS · CNES', status: 'disponivel' },
  { Icon: Map, name: 'Mercado UF / Município', desc: 'Cobertura e concentração regional, derivado das bases públicas.', source: 'Derivado HealthIntel', status: 'disponivel' },
  { Icon: TrendingUp, name: 'Rankings & Score', desc: 'Crescimento, oportunidade e score composto por operadora.', source: 'Modelo HealthIntel', status: 'disponivel' },
  { Icon: Gauge, name: 'DIOPS / FIP', desc: 'Documento de informações periódicas: financeiro das operadoras.', source: 'ANS · DIOPS / FIP', status: 'disponivel' },
  { Icon: Sparkles, name: 'IDSS', desc: 'Índice de Desempenho da Saúde Suplementar por operadora.', source: 'ANS · IDSS', status: 'disponivel' },
  { Icon: AlertTriangle, name: 'NIP', desc: 'Notificações de Intermediação Preliminar por operadora.', source: 'ANS · NIP', status: 'disponivel' },
  { Icon: BookOpen, name: 'Reajustes', desc: 'Histórico de reajustes autorizados por operadora e plano.', source: 'ANS · Reajustes', status: 'disponivel' },
  { Icon: Landmark, name: 'Rol / TUSS', desc: 'Rol de Procedimentos e Eventos em Saúde + tabela TUSS.', source: 'ANS · Rol · TUSS', status: 'disponivel' },
  { Icon: Shield, name: 'Garantias Financeiras', desc: 'Suficiência patrimonial e provisões técnicas das operadoras.', source: 'ANS · DIOPS', status: 'disponivel' },
  { Icon: Key, name: 'TISS / SIB individual', desc: 'Tabelas TISS e SIB nível beneficiário individual.', source: 'ANS · Acesso restrito', status: 'solicitacao' },
];

const STATUS_LABEL: Record<DatasetStatus, string> = {
  disponivel: 'Disponível',
  solicitacao: 'Sob solicitação',
};

function StatusPill({ status }: { status: DatasetStatus }) {
  return <span className={`status-pill status-pill--${status}`}>{STATUS_LABEL[status]}</span>;
}

export function DatasetsGrid() {
  return (
    <div className="datasets-grid">
      {DATASETS.map((d) => (
        <article key={d.name} className="dataset-card">
          <div className="dataset-card__top">
            <span className="icon-tile">
              <d.Icon size={16} />
            </span>
            <StatusPill status={d.status} />
          </div>
          <h3 className="dataset-card__name">{d.name}</h3>
          <p className="dataset-card__desc">{d.desc}</p>
          <p className="dataset-card__source mono">{d.source}</p>
        </article>
      ))}
    </div>
  );
}
