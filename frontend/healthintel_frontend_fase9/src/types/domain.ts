export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type EndpointTier = 'core' | 'premium' | 'admin' | 'interno' | 'sob_demanda';

export interface ApiEndpoint {
  id: string;
  method: HttpMethod;
  path: string;
  title: string;
  description: string;
  group: string;
  tier: EndpointTier;
  authRequired: boolean;
  exampleQuery?: Record<string, string | number>;
}

export interface DatasetStatus {
  codigo: string;
  nome: string;
  camada: 'api' | 'consumo' | 'interno';
  status: 'ativo' | 'em_validacao' | 'sob_demanda';
  atualizacao: string;
  retencao: string;
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
  preco: string;
  descricao: string;
  destaque?: boolean;
  features: string[];
  limits: string[];
  stripePaymentLink?: string;
  planoBd?: string;
}

export interface PortalUser {
  nome: string;
  email: string;
  empresa: string;
  cargo: string;
  plano: string;
  apiKey?: string;
}
