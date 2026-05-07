import type { ApiEndpoint } from '../types/domain';

export const endpointCatalog: ApiEndpoint[] = [
  {
    id: 'saude',
    method: 'GET',
    path: '/saude',
    title: 'Saúde da API',
    description: 'Verifica se a API está online e retorna ambiente, versão e dependências.',
    group: 'Sistema',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'prontidao',
    method: 'GET',
    path: '/prontidao',
    title: 'Prontidão',
    description: 'Verifica conectividade com dependências críticas.',
    group: 'Sistema',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'meta-dataset',
    method: 'GET',
    path: '/v1/meta/dataset',
    title: 'Catálogo de datasets',
    description: 'Lista datasets, status de publicação e metadados de atualização.',
    group: 'Metadados',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'meta-versao',
    method: 'GET',
    path: '/v1/meta/versao',
    title: 'Versão da plataforma',
    description: 'Retorna versão técnica e versão de dados publicada.',
    group: 'Metadados',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'meta-pipeline',
    method: 'GET',
    path: '/v1/meta/pipeline',
    title: 'Status do pipeline',
    description: 'Resumo de execução de ingestão, qualidade e publicação.',
    group: 'Metadados',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'meta-endpoints',
    method: 'GET',
    path: '/v1/meta/endpoints',
    title: 'Endpoints disponíveis',
    description: 'Lista endpoints publicados pela API.',
    group: 'Metadados',
    tier: 'core',
    authRequired: false
  },
  {
    id: 'operadoras',
    method: 'GET',
    path: '/v1/operadoras',
    title: 'Buscar operadoras',
    description: 'Consulta operadoras por UF, modalidade, nome, situação ou paginação.',
    group: 'Operadoras',
    tier: 'core',
    authRequired: true,
    exampleQuery: { uf: 'SP', limite: 20 }
  },
  {
    id: 'operadora-detalhe',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}',
    title: 'Detalhe da operadora',
    description: 'Retorna visão consolidada de uma operadora pelo registro ANS.',
    group: 'Operadoras',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'operadora-score',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score',
    title: 'Score da operadora',
    description: 'Score comercial/regulatório da operadora.',
    group: 'Operadoras',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'operadora-score-v3',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-v3',
    title: 'Score v3 da operadora',
    description: 'Score avançado com critérios consolidados.',
    group: 'Operadoras',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'operadora-score-v3-historico',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-v3/historico',
    title: 'Histórico de score v3',
    description: 'Evolução histórica do score da operadora.',
    group: 'Operadoras',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'operadora-regulatorio',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/regulatorio',
    title: 'Visão regulatória',
    description: 'Indicadores regulatórios da operadora.',
    group: 'Regulatório',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'score-regulatorio',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-regulatorio',
    title: 'Score regulatório',
    description: 'Score regulatório consolidado.',
    group: 'Regulatório',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'regime-especial',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/regime-especial',
    title: 'Regime especial',
    description: 'Consulta sinais de regime especial, direção fiscal/técnica ou liquidação.',
    group: 'Regulatório',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'portabilidade',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/portabilidade',
    title: 'Portabilidade',
    description: 'Consulta indicadores de portabilidade/regulação quando disponíveis.',
    group: 'Regulatório',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'rn623',
    method: 'GET',
    path: '/v1/regulatorio/rn623',
    title: 'RN 623',
    description: 'Consulta dados regulatórios mapeados conforme produto.',
    group: 'Regulatório',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'financeiro',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/financeiro',
    title: 'Financeiro da operadora',
    description: 'Indicadores financeiros e trimestrais da operadora.',
    group: 'Financeiro',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'score-v2',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-v2',
    title: 'Score financeiro v2',
    description: 'Score financeiro/regulatório v2.',
    group: 'Financeiro',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'mercado-municipio',
    method: 'GET',
    path: '/v1/mercado/municipio',
    title: 'Mercado por município',
    description: 'Consulta mercado por município, UF, competência ou filtros comerciais.',
    group: 'Mercado',
    tier: 'core',
    authRequired: true,
    exampleQuery: { uf: 'SP', limite: 20 }
  },
  {
    id: 'vazio-assistencial',
    method: 'GET',
    path: '/v1/mercado/vazio-assistencial',
    title: 'Vazio assistencial',
    description: 'Identifica oportunidades e gaps de oferta assistencial por região.',
    group: 'Mercado',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'ranking-score',
    method: 'GET',
    path: '/v1/rankings/operadora/score',
    title: 'Ranking por score',
    description: 'Ranking das operadoras por score consolidado.',
    group: 'Rankings',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'ranking-crescimento',
    method: 'GET',
    path: '/v1/rankings/operadora/crescimento',
    title: 'Ranking de crescimento',
    description: 'Ranking de crescimento ou queda de beneficiários.',
    group: 'Rankings',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'ranking-oportunidade',
    method: 'GET',
    path: '/v1/rankings/municipio/oportunidade',
    title: 'Oportunidade por município',
    description: 'Municípios priorizados por potencial comercial.',
    group: 'Rankings',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'ranking-oportunidade-v2',
    method: 'GET',
    path: '/v1/rankings/municipio/oportunidade-v2',
    title: 'Oportunidade por município v2',
    description: 'Versão aprimorada do ranking de oportunidades.',
    group: 'Rankings',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'ranking-composto',
    method: 'GET',
    path: '/v1/rankings/composto',
    title: 'Ranking composto',
    description: 'Ranking consolidado combinando múltiplas dimensões.',
    group: 'Rankings',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'rede-municipio',
    method: 'GET',
    path: '/v1/rede/municipio/{cd_municipio}',
    title: 'Rede assistencial por município',
    description: 'Resumo de rede assistencial agregada por município.',
    group: 'Rede Assistencial',
    tier: 'core',
    authRequired: true
  },
  {
    id: 'cnes-municipio',
    method: 'GET',
    path: '/v1/cnes/municipio/{cd_municipio}',
    title: 'CNES por município',
    description: 'Consulta estabelecimentos CNES agregados por município, tipo de unidade, leitos e vínculo SUS.',
    group: 'CNES',
    tier: 'core',
    authRequired: true,
    exampleQuery: { por_pagina: 20 }
  },
  {
    id: 'cnes-uf',
    method: 'GET',
    path: '/v1/cnes/uf/{sg_uf}',
    title: 'CNES por UF',
    description: 'Consulta estabelecimentos CNES consolidados por UF e tipo de unidade.',
    group: 'CNES',
    tier: 'core',
    authRequired: true,
    exampleQuery: { por_pagina: 20 }
  },
  {
    id: 'tiss-procedimentos',
    method: 'GET',
    path: '/v1/tiss/{registro_ans}/procedimentos',
    title: 'TISS procedimentos',
    description: 'Endpoint TISS fora do produto inicial por custo/tamanho operacional.',
    group: 'TISS',
    tier: 'sob_demanda',
    authRequired: true
  },
  {
    id: 'tiss-sinistralidade',
    method: 'GET',
    path: '/v1/tiss/{registro_ans}/sinistralidade',
    title: 'TISS sinistralidade',
    description: 'Endpoint TISS fora do produto inicial por custo/tamanho operacional.',
    group: 'TISS',
    tier: 'sob_demanda',
    authRequired: true
  },
  {
    id: 'premium-operadoras',
    method: 'GET',
    path: '/v1/premium/operadoras',
    title: 'Premium operadoras',
    description: 'Endpoint premium disponível apenas por contratação específica.',
    group: 'Premium',
    tier: 'premium',
    authRequired: true
  },
  {
    id: 'admin-billing-resumo',
    method: 'GET',
    path: '/admin/billing/resumo',
    title: 'Resumo de billing',
    description: 'Endpoint administrativo para fechamento e acompanhamento de faturamento.',
    group: 'Admin',
    tier: 'admin',
    authRequired: true,
    exampleQuery: { referencia: '2026-05' }
  },
  {
    id: 'admin-layouts',
    method: 'GET',
    path: '/admin/layouts',
    title: 'Administração de layouts',
    description: 'Gestão interna de layouts e compatibilidades de arquivos.',
    group: 'Admin',
    tier: 'admin',
    authRequired: true
  }
];

export const coreEndpoints = endpointCatalog.filter((endpoint) => endpoint.tier === 'core');
export const publicDocumentationEndpoints = endpointCatalog.filter((endpoint) => endpoint.tier === 'core');
export const liveTesterEndpoints = endpointCatalog.filter((endpoint) => endpoint.tier === 'core');
