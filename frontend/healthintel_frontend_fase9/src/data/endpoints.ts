import type { ApiEndpoint } from '../types/domain';

export const endpointStatusLabel = {
  disponivel: 'Disponivel',
  parcial: 'Parcial',
  roadmap: 'Roadmap',
  sem_dados: 'Sem dados',
  premium: 'Premium'
} as const;

export const endpointCatalog: ApiEndpoint[] = [
  {
    id: 'saude',
    method: 'GET',
    path: '/saude',
    title: 'Saude da API',
    description: 'Verifica se a API esta online.',
    group: 'Sistema',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'prontidao',
    method: 'GET',
    path: '/prontidao',
    title: 'Prontidao',
    description: 'Verifica conectividade com dependencias criticas.',
    group: 'Sistema',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'meta-dataset',
    method: 'GET',
    path: '/v1/meta/dataset',
    title: 'Catalogo de datasets',
    description: 'Lista datasets, status de publicacao e metadados de atualizacao.',
    group: 'Metadados',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'meta-versao',
    method: 'GET',
    path: '/v1/meta/versao',
    title: 'Versao da plataforma',
    description: 'Retorna versao tecnica e versao de dados publicada.',
    group: 'Metadados',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'meta-pipeline',
    method: 'GET',
    path: '/v1/meta/pipeline',
    title: 'Status do pipeline',
    description: 'Resumo de execucao de ingestao, qualidade e publicacao.',
    group: 'Metadados',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'meta-endpoints',
    method: 'GET',
    path: '/v1/meta/endpoints',
    title: 'Endpoints disponiveis',
    description: 'Lista endpoints publicados pela API.',
    group: 'Metadados',
    tier: 'core',
    availability: 'disponivel',
    authRequired: false
  },
  {
    id: 'operadoras',
    method: 'GET',
    path: '/v1/operadoras',
    title: 'Buscar operadoras',
    description: 'Consulta operadoras por UF, modalidade, nome, situacao ou paginacao.',
    group: 'Operadoras',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true,
    exampleQuery: { uf: 'SP', limite: 20 }
  },
  {
    id: 'operadora-detalhe',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}',
    title: 'Detalhe da operadora',
    description: 'Retorna visao consolidada de uma operadora pelo registro ANS.',
    group: 'Operadoras',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'operadora-beneficiarios',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/beneficiarios',
    title: 'Beneficiarios da operadora',
    description: 'Beneficiarios agregados por operadora e competencia.',
    group: 'Operadoras',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'operadora-score-v3',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-v3',
    title: 'Score v3 da operadora',
    description: 'Score avancado com componentes consolidados.',
    group: 'Score',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'operadora-score-v3-historico',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/score-v3/historico',
    title: 'Historico de score v3',
    description: 'Evolucao historica do score da operadora.',
    group: 'Score',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'operadora-regulatorio',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/regulatorio',
    title: 'Visao regulatoria',
    description: 'Indicadores regulatorios consolidados da operadora.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'operadora-financeiro',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/financeiro',
    title: 'Financeiro da operadora',
    description: 'Indicadores financeiros e trimestrais da operadora.',
    group: 'Financeiro',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'mercado-municipio',
    method: 'GET',
    path: '/v1/mercado/municipio',
    title: 'Mercado por municipio',
    description: 'Consulta mercado por municipio, UF, competencia e filtros comerciais.',
    group: 'Mercado',
    tier: 'core',
    availability: 'parcial',
    authRequired: true,
    exampleQuery: { uf: 'SP', limite: 20 }
  },
  {
    id: 'ranking-score',
    method: 'GET',
    path: '/v1/rankings/operadora/score',
    title: 'Ranking por score',
    description: 'Ranking das operadoras por score consolidado.',
    group: 'Rankings',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'ranking-crescimento',
    method: 'GET',
    path: '/v1/rankings/operadora/crescimento',
    title: 'Ranking de crescimento',
    description: 'Ranking de crescimento ou queda de beneficiarios.',
    group: 'Rankings',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'ranking-oportunidade',
    method: 'GET',
    path: '/v1/rankings/municipio/oportunidade',
    title: 'Oportunidade por municipio',
    description: 'Municipios priorizados por potencial comercial.',
    group: 'Rankings',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'ranking-oportunidade-v2',
    method: 'GET',
    path: '/v1/rankings/municipio/oportunidade-v2',
    title: 'Oportunidade por municipio v2',
    description: 'Versao aprimorada do ranking de oportunidades.',
    group: 'Rankings',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'ranking-composto',
    method: 'GET',
    path: '/v1/rankings/composto',
    title: 'Ranking composto',
    description: 'Ranking consolidado combinando multiplas dimensoes.',
    group: 'Rankings',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'produtos-planos',
    method: 'GET',
    path: '/v1/produtos-planos',
    title: 'Produtos e planos',
    description: 'Produtos/planos ANS por operadora, situacao e segmentacao.',
    group: 'Produto/Plano',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'historico-planos',
    method: 'GET',
    path: '/v1/historico-planos',
    title: 'Historico de planos',
    description: 'Historico de situacao e caracteristicas de planos.',
    group: 'Produto/Plano',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'regulatorio',
    method: 'GET',
    path: '/v1/regulatorio',
    title: 'Regulatorio consolidado',
    description: 'Indicadores regulatorios agregados por operadora e periodo.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'igr',
    method: 'GET',
    path: '/v1/igr',
    title: 'IGR',
    description: 'Indice de Garantia de Resolutividade por operadora.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'nip',
    method: 'GET',
    path: '/v1/nip',
    title: 'NIP',
    description: 'Demandas NIP e taxa de resolutividade historica.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'idss',
    method: 'GET',
    path: '/v1/idss',
    title: 'IDSS',
    description: 'IDSS anual e dimensoes de desempenho da saude suplementar.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'financeiro',
    method: 'GET',
    path: '/v1/financeiro',
    title: 'Financeiro consolidado',
    description: 'Consulta financeira paginada por operadora e periodo.',
    group: 'Financeiro',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'prudencial',
    method: 'GET',
    path: '/v1/prudencial',
    title: 'Prudencial',
    description: 'Indicadores prudenciais e situacao de capital/liquidez.',
    group: 'Financeiro',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'regime-especial',
    method: 'GET',
    path: '/v1/regime-especial',
    title: 'Regime especial',
    description: 'Historico de regimes especiais por operadora.',
    group: 'Regulatorio',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'glosa',
    method: 'GET',
    path: '/v1/glosa',
    title: 'Glosa',
    description: 'Valores e taxas de glosa por operadora e competencia.',
    group: 'Financeiro',
    tier: 'core',
    availability: 'parcial',
    authRequired: true
  },
  {
    id: 'rn623',
    method: 'GET',
    path: '/v1/regulatorio/rn623',
    title: 'RN 623',
    description: 'Endpoint criado para dados regulatorios especificos; sem carga completa no release.',
    group: 'Roadmap',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'portabilidade',
    method: 'GET',
    path: '/v1/operadoras/{registro_ans}/portabilidade',
    title: 'Portabilidade',
    description: 'Indicadores de portabilidade quando disponiveis.',
    group: 'Roadmap',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'vazio-assistencial',
    method: 'GET',
    path: '/v1/mercado/vazio-assistencial',
    title: 'Vazio assistencial',
    description: 'Oportunidades e gaps assistenciais por regiao.',
    group: 'Roadmap',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'rede-municipio',
    method: 'GET',
    path: '/v1/rede/municipio/{cd_municipio}',
    title: 'Rede assistencial por municipio',
    description: 'Resumo de rede assistencial agregada por municipio.',
    group: 'Rede/CNES',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'cnes-municipio',
    method: 'GET',
    path: '/v1/cnes/municipio/{cd_municipio}',
    title: 'CNES por municipio',
    description: 'Estabelecimentos CNES consolidados por municipio.',
    group: 'Rede/CNES',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'cnes-uf',
    method: 'GET',
    path: '/v1/cnes/uf/{sg_uf}',
    title: 'CNES por UF',
    description: 'Estabelecimentos CNES consolidados por UF.',
    group: 'Rede/CNES',
    tier: 'sob_demanda',
    availability: 'roadmap',
    authRequired: true
  },
  {
    id: 'tuss-procedimentos',
    method: 'GET',
    path: '/v1/tuss/procedimentos',
    title: 'TUSS procedimentos',
    description: 'Terminologia TUSS vigente.',
    group: 'TISS/TUSS',
    tier: 'core',
    availability: 'disponivel',
    authRequired: true
  },
  {
    id: 'tiss-procedimentos',
    method: 'GET',
    path: '/v1/tiss/{registro_ans}/procedimentos',
    title: 'TISS procedimentos',
    description: 'Endpoint TISS fora do produto recorrente atual.',
    group: 'Roadmap',
    tier: 'sob_demanda',
    availability: 'sem_dados',
    authRequired: true
  },
  {
    id: 'tiss-sinistralidade',
    method: 'GET',
    path: '/v1/tiss/{registro_ans}/sinistralidade',
    title: 'TISS sinistralidade',
    description: 'Endpoint TISS fora do produto recorrente atual.',
    group: 'Roadmap',
    tier: 'sob_demanda',
    availability: 'sem_dados',
    authRequired: true
  },
  {
    id: 'premium-operadoras',
    method: 'GET',
    path: '/v1/premium/operadoras',
    title: 'Premium operadoras',
    description: 'Operadora 360 validada com MDM e qualidade documental.',
    group: 'Premium',
    tier: 'premium',
    availability: 'premium',
    authRequired: true
  },
  {
    id: 'premium-mdm-operadoras',
    method: 'GET',
    path: '/v1/premium/mdm/operadoras',
    title: 'MDM operadoras',
    description: 'Golden record premium de operadoras.',
    group: 'Premium',
    tier: 'premium',
    availability: 'premium',
    authRequired: true
  },
  {
    id: 'premium-mdm-prestadores',
    method: 'GET',
    path: '/v1/premium/mdm/prestadores',
    title: 'MDM prestadores',
    description: 'Golden record premium de prestadores.',
    group: 'Premium',
    tier: 'premium',
    availability: 'premium',
    authRequired: true
  },
  {
    id: 'premium-quality',
    method: 'GET',
    path: '/v1/premium/quality/datasets',
    title: 'Quality datasets',
    description: 'Resumo de qualidade documental premium.',
    group: 'Premium',
    tier: 'premium',
    availability: 'premium',
    authRequired: true
  },
  {
    id: 'premium-tuss',
    method: 'GET',
    path: '/v1/premium/tuss/procedimentos',
    title: 'Premium TUSS',
    description: 'Crosswalk TISS/TUSS com score de qualidade.',
    group: 'Premium',
    tier: 'premium',
    availability: 'premium',
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
    availability: 'disponivel',
    authRequired: true,
    exampleQuery: { referencia: '2026-05' }
  },
  {
    id: 'admin-layouts',
    method: 'GET',
    path: '/admin/layouts',
    title: 'Administracao de layouts',
    description: 'Gestao interna de layouts e compatibilidades de arquivos.',
    group: 'Admin',
    tier: 'admin',
    availability: 'disponivel',
    authRequired: true
  }
];

export const coreEndpoints = endpointCatalog.filter((endpoint) => endpoint.tier === 'core');
export const publicDocumentationEndpoints = endpointCatalog.filter((endpoint) => endpoint.tier !== 'admin');
export const liveTesterEndpoints = endpointCatalog.filter((endpoint) =>
  endpoint.authRequired && endpoint.tier === 'core' && endpoint.availability !== 'roadmap' && endpoint.availability !== 'sem_dados'
);
