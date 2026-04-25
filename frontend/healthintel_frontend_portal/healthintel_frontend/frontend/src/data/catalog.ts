export type TierKey =
  | "piloto"
  | "essencial"
  | "plus"
  | "enterprise"
  | "enterprise_tecnico";

export type EndpointItem = {
  method: "GET" | "POST";
  path: string;
  auth: boolean;
  tier: string;
  layer: "Público" | "Ouro" | "Prata" | "Bronze" | "Admin";
  description: string;
  samplePath: string;
};

export const tiers = [
  {
    key: "piloto",
    name: "Piloto",
    price: "R$ 0–299",
    subtitle: "Validação técnica e POC",
    layer: "Ouro",
    requests: "Baixo volume",
    sla: "SLA básico",
    cta: "Começar validação",
    highlighted: false,
    features: [
      "Acesso à camada Ouro",
      "Operadoras, rankings e scores essenciais",
      "Chave de API para teste",
      "Ideal para validar aderência do produto"
    ]
  },
  {
    key: "essencial",
    name: "Essencial",
    price: "R$ 499–999",
    subtitle: "Produto padrão para consumo B2B",
    layer: "Ouro",
    requests: "Volume médio",
    sla: "SLA básico",
    cta: "Assinar Essencial",
    highlighted: true,
    features: [
      "Scores, rankings e séries históricas",
      "Endpoints prontos para produto e engenharia",
      "Rate limit comercial",
      "Suporte técnico de integração"
    ]
  },
  {
    key: "plus",
    name: "Plus",
    price: "R$ 1.499–2.999",
    subtitle: "Dados padronizados + ouro",
    layer: "Ouro + Prata",
    requests: "Volume médio/alto",
    sla: "SLA intermediário",
    cta: "Falar com vendas",
    highlighted: false,
    features: [
      "Acesso à camada Prata",
      "Taxa de aprovação por lote",
      "Registros em quarentena agregados",
      "Dados enriquecidos por município e operadora"
    ]
  },
  {
    key: "enterprise",
    name: "Enterprise",
    price: "Sob contrato",
    subtitle: "Acesso completo por camada",
    layer: "Ouro + Prata + Bronze",
    requests: "Alto volume",
    sla: "SLA forte",
    cta: "Contratar Enterprise",
    highlighted: false,
    features: [
      "Acesso completo às três camadas",
      "Metadados de auditoria",
      "Contratos de SLA por camada",
      "Suporte prioritário"
    ]
  },
  {
    key: "enterprise_tecnico",
    name: "Enterprise Técnico",
    price: "Sob contrato",
    subtitle: "Infraestrutura de dados para engenharia",
    layer: "Ouro + Prata + Bronze",
    requests: "Sem limite comercial padrão",
    sla: "SLA máximo",
    cta: "Desenhar contrato",
    highlighted: false,
    features: [
      "Bronze API com rastreabilidade total",
      "Hash de arquivo e linha",
      "Versão de layout e lote de ingestão",
      "Uso como infraestrutura própria do cliente"
    ]
  }
];

export const endpointCatalog: EndpointItem[] = [
  {
    method: "GET",
    path: "/saude",
    auth: false,
    tier: "Público",
    layer: "Público",
    description: "Health check simples da aplicação.",
    samplePath: "/saude"
  },
  {
    method: "GET",
    path: "/prontidao",
    auth: false,
    tier: "Público",
    layer: "Público",
    description: "Prontidão da API e dependências.",
    samplePath: "/prontidao"
  },
  {
    method: "GET",
    path: "/v1/meta/endpoints",
    auth: false,
    tier: "Público",
    layer: "Público",
    description: "Catálogo interno de endpoints expostos.",
    samplePath: "/v1/meta/endpoints"
  },
  {
    method: "GET",
    path: "/v1/operadoras",
    auth: true,
    tier: "Starter/Essencial",
    layer: "Ouro",
    description: "Lista operadoras com filtros por busca, UF e modalidade.",
    samplePath: "/v1/operadoras?pagina=1&por_pagina=10"
  },
  {
    method: "GET",
    path: "/v1/operadoras/{registro_ans}",
    auth: true,
    tier: "Starter/Essencial",
    layer: "Ouro",
    description: "Detalha uma operadora por registro ANS.",
    samplePath: "/v1/operadoras/123456"
  },
  {
    method: "GET",
    path: "/v1/operadoras/{registro_ans}/score-v3",
    auth: true,
    tier: "Essencial",
    layer: "Ouro",
    description: "Consulta o Score v3 composto por operadora.",
    samplePath: "/v1/operadoras/123456/score-v3?competencia=202501"
  },
  {
    method: "GET",
    path: "/v1/operadoras/{registro_ans}/score-v3/historico",
    auth: true,
    tier: "Essencial",
    layer: "Ouro",
    description: "Histórico do Score v3.",
    samplePath: "/v1/operadoras/123456/score-v3/historico?periodos=12"
  },
  {
    method: "GET",
    path: "/v1/mercado/municipio",
    auth: true,
    tier: "Starter/Essencial",
    layer: "Ouro",
    description: "Mercado por município com filtros de UF, competência e segmento.",
    samplePath: "/v1/mercado/municipio?uf=SP&competencia=202501&pagina=1&por_pagina=10"
  },
  {
    method: "GET",
    path: "/v1/mercado/vazio-assistencial",
    auth: true,
    tier: "Growth/Plus",
    layer: "Ouro",
    description: "Identifica vazios assistenciais por território.",
    samplePath: "/v1/mercado/vazio-assistencial?uf=SP&pagina=1&por_pagina=10"
  },
  {
    method: "GET",
    path: "/v1/cnes/municipio/{cd_municipio}",
    auth: true,
    tier: "Growth/Plus",
    layer: "Ouro",
    description: "Estabelecimentos CNES por município.",
    samplePath: "/v1/cnes/municipio/3550308"
  },
  {
    method: "GET",
    path: "/v1/tiss/{registro_ans}/procedimentos",
    auth: true,
    tier: "Growth/Plus",
    layer: "Ouro",
    description: "Procedimentos TISS por operadora.",
    samplePath: "/v1/tiss/123456/procedimentos"
  },
  {
    method: "GET",
    path: "/v1/prata/*",
    auth: true,
    tier: "Analítico/Plus",
    layer: "Prata",
    description: "Endpoints padronizados com taxa de aprovação e quarentena.",
    samplePath: "/v1/prata/cadop?pagina=1&por_pagina=10"
  },
  {
    method: "GET",
    path: "/v1/bronze/*",
    auth: true,
    tier: "Enterprise Técnico",
    layer: "Bronze",
    description: "Dado bruto auditável com metadados de lote, arquivo e layout.",
    samplePath: "/v1/bronze/cadop?pagina=1&por_pagina=10"
  },
  {
    method: "GET",
    path: "/admin/billing/resumo",
    auth: true,
    tier: "Admin",
    layer: "Admin",
    description: "Resumo de faturamento por referência.",
    samplePath: "/admin/billing/resumo?referencia=2026-04"
  }
];

export const layerCards = [
  {
    name: "Bronze",
    schema: "bruto_ans",
    contract: "Dado bruto auditável",
    copy: "Para engenharia, auditoria, reprocessamento e rastreabilidade de arquivo até linha."
  },
  {
    name: "Prata",
    schema: "stg_ans / int_ans",
    contract: "Dado tipado e padronizado",
    copy: "Para times de dados que precisam de tipos, domínios, qualidade e quarentena transparente."
  },
  {
    name: "Ouro",
    schema: "api_ans",
    contract: "Dado pronto para integração",
    copy: "Para produtos, squads B2B, pricing, risco, regulatório e inteligência comercial."
  }
];
