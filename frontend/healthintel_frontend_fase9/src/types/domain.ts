export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type EndpointTier = 'core' | 'premium' | 'admin' | 'interno' | 'sob_demanda';
export type DeliveryStatus = 'pronto' | 'parcial' | 'premium' | 'roadmap' | 'sem_dados';
export type EndpointAvailability = 'disponivel' | 'parcial' | 'premium' | 'roadmap' | 'sem_dados';

export interface ApiEndpoint {
  id: string;
  method: HttpMethod;
  path: string;
  title: string;
  description: string;
  group: string;
  tier: EndpointTier;
  availability?: EndpointAvailability;
  authRequired: boolean;
  exampleQuery?: Record<string, string | number>;
}

export interface DatasetStatus {
  codigo: string;
  nome: string;
  dominio: string;
  schema: 'consumo_ans' | 'consumo_premium_ans' | 'api_ans' | 'nucleo_ans' | 'meta';
  tabela: string;
  camada: 'api' | 'consumo' | 'premium' | 'interno';
  status: DeliveryStatus;
  linhas: string;
  periodos: string;
  janela: string;
  atualizacao: string;
  grao: string;
  extracao: string;
  usoComercial: string;
  descricao: string;
}

export interface UsagePoint {
  dia: string;
  requisicoes: number;
  erros: number;
  latenciaMs: number;
}

export interface ApiPlan {
  nome: string;
  slug: string;
  preco: string;
  descricao: string;
  destaque?: boolean;
  features: string[];
  limits: string[];
  stripePaymentLink?: string;
  planoBd?: string;
  checkoutSlug?: 'sandbox' | 'piloto' | 'core';
}

export interface PortalUser {
  nome: string;
  email: string;
  empresa: string;
  cargo: string;
  plano: string;
  role?: 'admin' | 'member';
  apiKey?: string;
}
