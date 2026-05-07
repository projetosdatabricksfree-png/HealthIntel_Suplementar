import type { DatasetStatus } from '../types/domain';

export const datasets: DatasetStatus[] = [
  {
    codigo: 'cadop',
    nome: 'Cadastro de Operadoras',
    camada: 'api',
    status: 'ativo',
    atualizacao: 'mensal / conforme ANS',
    retencao: 'versão vigente + histórico leve',
    descricao: 'Cadastro, registro ANS, razão social, modalidade, UF e situação.'
  },
  {
    codigo: 'sib',
    nome: 'Beneficiários SIB',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'mensal',
    retencao: '12 a 24 meses no plano Core',
    descricao: 'Beneficiários por operadora, município e competência.'
  },
  {
    codigo: 'idss',
    nome: 'IDSS',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'anual',
    retencao: 'histórico completo se leve',
    descricao: 'Indicadores de desempenho das operadoras.'
  },
  {
    codigo: 'igr',
    nome: 'IGR',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'conforme publicação',
    retencao: 'histórico leve',
    descricao: 'Indicadores regulatórios e de governança.'
  },
  {
    codigo: 'nip',
    nome: 'NIP',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'mensal/trimestral',
    retencao: '24 a 36 meses',
    descricao: 'Indicadores de reclamações e atendimento.'
  },
  {
    codigo: 'financeiro',
    nome: 'DIOPS/FIP',
    camada: 'consumo',
    status: 'em_validacao',
    atualizacao: 'trimestral',
    retencao: '8 a 12 trimestres',
    descricao: 'Receitas, despesas, resultado, índices e sinais financeiros.'
  },
  {
    codigo: 'rn623',
    nome: 'RN 623',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'conforme publicação',
    retencao: 'histórico regulatório leve',
    descricao: 'Enquadramentos e informações regulatórias relevantes para análise de operadoras.'
  },
  {
    codigo: 'regime_especial',
    nome: 'Regime Especial',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'conforme publicação',
    retencao: 'histórico regulatório estendido',
    descricao: 'Sinais de direção fiscal, direção técnica, liquidação e acompanhamento regulatório.'
  },
  {
    codigo: 'portabilidade',
    nome: 'Portabilidade',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'mensal / conforme ANS',
    retencao: '24 a 36 meses',
    descricao: 'Movimentações e sinais de portabilidade para leitura competitiva do mercado.'
  },
  {
    codigo: 'rede_assistencial',
    nome: 'Rede Assistencial',
    camada: 'consumo',
    status: 'ativo',
    atualizacao: 'mensal / conforme disponibilidade',
    retencao: '12 a 24 meses',
    descricao: 'Cobertura agregada de rede por município e suporte a análises de vazio assistencial.'
  },
  {
    codigo: 'cnes_estabelecimento',
    nome: 'CNES Estabelecimentos',
    camada: 'api',
    status: 'ativo',
    atualizacao: 'mensal / conforme DATASUS',
    retencao: 'snapshot vigente + histórico leve',
    descricao: 'Estabelecimentos de saúde por município e UF, com tipo de unidade, leitos e vínculo SUS.'
  },
  {
    codigo: 'mercado_municipio',
    nome: 'Mercado por Município',
    camada: 'api',
    status: 'ativo',
    atualizacao: 'mensal',
    retencao: '12 a 24 meses',
    descricao: 'Market share, concentração, oportunidade territorial e leitura regional.'
  },
  {
    codigo: 'score_v3',
    nome: 'Score HealthIntel',
    camada: 'api',
    status: 'ativo',
    atualizacao: 'mensal / conforme atualização das fontes',
    retencao: 'histórico leve',
    descricao: 'Score composto com dimensões regulatória, financeira, estrutural e de mercado.'
  },
  {
    codigo: 'ranking_composto',
    nome: 'Rankings Comerciais',
    camada: 'api',
    status: 'ativo',
    atualizacao: 'mensal',
    retencao: 'histórico leve',
    descricao: 'Rankings de score, crescimento, oportunidade municipal e posição competitiva.'
  },
  {
    codigo: 'tiss',
    nome: 'TISS',
    camada: 'interno',
    status: 'sob_demanda',
    atualizacao: 'não publicado',
    retencao: 'expansão contratada',
    descricao: 'Módulo analítico avançado para estudos de utilização, procedimentos e sinistralidade.'
  },
  {
    codigo: 'cnes',
    nome: 'Rede e Cobertura Avançada',
    camada: 'interno',
    status: 'sob_demanda',
    atualizacao: 'não publicado',
    retencao: 'expansão contratada',
    descricao: 'Pacote analítico para cruzamentos dedicados, filtros avançados e recortes regionais específicos.'
  }
];
