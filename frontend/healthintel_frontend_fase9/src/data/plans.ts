import type { ApiPlan, PlanSlug } from '../types/domain';
import { commercialLinks } from '../config/commercialLinks';

export const plans: ApiPlan[] = [
  {
    nome: 'FREE',
    slug: 'free',
    preco: 'R$ 0',
    descricao: 'Ambiente gratuito para avaliacao tecnica sem cartao.',
    limiteDiario: '100 req/dia',
    keyLimit: 1,
    teamLimit: 0,
    features: [
      'Endpoints Core em leitura',
      '1 API key de teste',
      'Ambiente test/free',
      'Login com Google',
      'Quickstart com cURL'
    ],
    limits: [
      'Sem uso comercial',
      'Sem equipe',
      'Sem logs exportaveis'
    ],
    planoBd: 'free'
  },
  {
    nome: 'STARTER',
    slug: 'starter',
    preco: 'R$ 99,99/mês',
    descricao: 'Integracao inicial para validar consumo recorrente da API.',
    limiteDiario: '30.000 req/dia',
    keyLimit: 1,
    teamLimit: 0,
    features: [
      'Core + derivados publicados',
      '1 API key live/test',
      '2FA pessoal',
      'Logs basicos no portal',
      'Suporte por e-mail async'
    ],
    limits: [
      'Sem equipe',
      'Sem IP allowlist',
      'Sem exportacao de logs'
    ],
    planoBd: 'starter',
    checkoutSlug: 'starter',
    stripePaymentLink: commercialLinks.stripe.starter || undefined,
  },
  {
    nome: 'PRO',
    slug: 'pro',
    preco: 'R$ 499/mês',
    descricao: 'Producao padrao para BI, dados e produtos digitais.',
    destaque: true,
    limiteDiario: '150.000 req/dia',
    keyLimit: 3,
    teamLimit: 3,
    features: [
      'Todos os datasets publicados',
      '3 API keys live/test',
      'Equipe com ate 3 usuarios',
      'Logs exportaveis CSV/JSON',
      'IP allowlist'
    ],
    limits: [
      'Sem SSO/SAML',
      'Sem SLA contratual'
    ],
    planoBd: 'pro',
    checkoutSlug: 'pro',
    stripePaymentLink: commercialLinks.stripe.pro || undefined,
  },
  {
    nome: 'MAX',
    slug: 'max',
    preco: 'R$ 1.499/mês',
    descricao: 'Alto volume para healthtechs, operadoras e times de produto.',
    limiteDiario: '500.000 req/dia',
    keyLimit: 5,
    teamLimit: 10,
    features: [
      'Tudo do PRO',
      '5 API keys',
      'Equipe com ate 10 usuarios',
      'Webhooks de uso',
      'Suporte com SLA de resposta'
    ],
    limits: [
      'SSO/SAML somente Enterprise',
      'Premium MDM por opt-in'
    ],
    planoBd: 'max',
    checkoutSlug: 'max',
    stripePaymentLink: commercialLinks.stripe.max || undefined,
  },
  {
    nome: 'ENTERPRISE',
    slug: 'enterprise',
    preco: 'Sob contrato',
    descricao: 'Volume contratual, SLA dedicado, SSO/SAML e requisitos customizados.',
    limiteDiario: 'Contratual',
    keyLimit: 'ilimitado',
    teamLimit: 'ilimitado',
    features: [
      'Limites e SLA sob contrato',
      'SSO/SAML',
      'IP allowlist com CIDR',
      'Retencao customizada',
      'Premium MDM incluso quando contratado'
    ],
    limits: [
      'Negociado off-checkout'
    ],
    planoBd: 'enterprise'
  }
];

export function getPlanBySlug(slug: PlanSlug): ApiPlan {
  return plans.find((plan) => plan.slug === slug) || plans[0];
}
