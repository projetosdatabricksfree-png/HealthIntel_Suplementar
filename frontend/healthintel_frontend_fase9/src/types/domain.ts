export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type EndpointTier = 'core' | 'premium' | 'admin' | 'interno' | 'sob_demanda';
export type DeliveryStatus = 'pronto' | 'parcial' | 'premium' | 'roadmap' | 'sem_dados';
export type EndpointAvailability = 'disponivel' | 'parcial' | 'premium' | 'roadmap' | 'sem_dados';
export type PlanSlug = 'free' | 'starter' | 'pro' | 'max' | 'enterprise';
export type PortalRole = 'admin_internal' | 'owner' | 'admin' | 'member' | 'reader';

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
  slug: PlanSlug;
  preco: string;
  precoAnual?: string;
  economiaAnual?: string | null;
  descricao: string;
  destaque?: boolean;
  limiteDiario: string;
  keyLimit: number | 'ilimitado';
  teamLimit: number | 'ilimitado' | 0;
  features: string[];
  limits: string[];
  stripePaymentLink?: string;
  planoBd: PlanSlug;
  checkoutSlug?: 'starter' | 'pro' | 'max';
}

export interface UsageDia {
  dia: string;
  requisicoes: number;
  erros: number;
  latencia_ms: number;
}

export interface UsageRealData {
  total_requisicoes: number;
  total_erros: number;
  latencia_media_ms: number;
  success_rate?: number;
  serie_diaria: UsageDia[];
  por_endpoint: Array<{ endpoint: string; requisicoes: number; erros: number }>;
}

export interface UsageMeta {
  periodo: string;
  inicio: string;
  fim: string;
  plano: string;
  quota_daily?: number;
  quota_used_today?: number;
  quota_monthly?: number;
  quota_used_month?: number | null;
  modelo_cobranca?: 'flat' | 'franquia_overage' | 'pay_as_you_go';
  trial_pro_ativo?: boolean;
  trial_pro_expira_em?: string | null;
}

export interface PortalUser {
  nome: string;
  email: string;
  empresa: string;
  cargo: string;
  plano: string;
  role?: PortalRole;
  apiKey?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  nome: string;
  avatar_url: string | null;
  status: string;
  email_verificado: boolean;
  tenants: AuthTenant[];
  tenant_ativo: AuthTenant | null;
}

export interface AuthTenant {
  cliente_id: string;
  nome: string;
  role: string;
  status: string;
  plano_nome: string;
}

export interface PortalApiKey {
  id: string;
  nome: string | null;
  prefixo: string;
  ambiente: 'sandbox' | 'producao';
  escopos: string[];
  status: string;
  criado_em: string;
  ultimo_uso_em: string | null;
  revogada_em: string | null;
  expira_em: string | null;
}

export interface BillingResumo {
  plano: {
    nome: string;
    limite_rpm: number;
    limite_api_keys: number;
  };
  assinatura: {
    status: string;
    stripe_subscription_id: string | null;
    current_period_end: string | null;
    cancel_at_period_end: boolean;
  } | null;
  uso_hoje: number;
  chaves_ativas: number;
}

export interface Fatura {
  id: string;
  numero: string | null;
  data: number;
  valor_centavos: number;
  moeda: string;
  status: string;
  pdf_url: string | null;
  descricao: string | null;
}

export interface TeamMember {
  id: string;
  email: string;
  nome: string;
  avatar_url: string | null;
  role: string;
  status: string;
  aceito_em: string | null;
  ultimo_login_em: string | null;
}
