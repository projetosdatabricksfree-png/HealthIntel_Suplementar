import type { ApiPlan, PlanSlug } from '../types/domain';
import { commercialLinks } from '../config/commercialLinks';

export const plans: ApiPlan[] = [
  {
    nome: 'FREE',
    slug: 'free',
    preco: 'R$ 0',
    precoAnual: 'R$ 0',
    economiaAnual: null,
    descricao: '14 dias de trial PRO ao cadastrar. Depois: 100 requisições/mês.',
    limiteDiario: '100 req/mês',
    keyLimit: 1,
    teamLimit: 0,
    features: [
      '14 dias de trial PRO (2.500 req/dia)',
      'Após trial: 100 req/mês para sempre',
      '1 API key de teste',
      'Login com Google',
      'Quickstart com cURL'
    ],
    limits: [
      'Sem uso comercial',
      'Sem equipe',
      'Sem logs exportáveis'
    ],
    planoBd: 'free'
  },
  {
    nome: 'STARTER',
    slug: 'starter',
    preco: 'R$ 99,99/mês',
    precoAnual: 'R$ 999,90/ano',
    economiaAnual: '2 meses grátis',
    descricao: 'Integração inicial para validar consumo recorrente da API.',
    limiteDiario: '500 req/dia',
    keyLimit: 3,
    teamLimit: 0,
    features: [
      'Core + derivados publicados',
      '3 API keys live/test',
      '2FA pessoal',
      'Logs básicos no portal',
      'Suporte por e-mail async'
    ],
    limits: [
      'Sem equipe',
      'Sem IP allowlist',
      'Sem exportação de logs'
    ],
    planoBd: 'starter',
    checkoutSlug: 'starter',
    stripePaymentLink: commercialLinks.stripe.starter || undefined,
  },
  {
    nome: 'PRO',
    slug: 'pro',
    preco: 'R$ 499/mês',
    precoAnual: 'R$ 4.990/ano',
    economiaAnual: '2 meses grátis',
    descricao: 'Produção padrão para BI, dados e produtos digitais.',
    destaque: true,
    limiteDiario: '2.500 req/dia',
    keyLimit: 10,
    teamLimit: 3,
    features: [
      'Todos os datasets publicados',
      '10 API keys live/test',
      'Equipe com até 3 usuários',
      'Logs exportáveis CSV/JSON',
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
    precoAnual: 'R$ 14.990/ano',
    economiaAnual: '2 meses grátis',
    descricao: 'Alto volume para healthtechs, operadoras e times de produto.',
    limiteDiario: '25.000 req/dia',
    keyLimit: 25,
    teamLimit: 10,
    features: [
      'Tudo do PRO',
      '25 API keys',
      'Equipe com até 10 usuários',
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
    preco: 'A partir de R$ 5.000/mês',
    precoAnual: 'Sob contrato',
    economiaAnual: null,
    descricao: 'Pay-as-you-go: mínimo R$ 5.000/mês + R$ 50 por mil req acima de 500k. SLA dedicado, SSO/SAML.',
    limiteDiario: 'Sem cap diário',
    keyLimit: 'ilimitado',
    teamLimit: 'ilimitado',
    features: [
      'Sem limite diário (pay-as-you-go)',
      'Mínimo R$ 5.000/mês cobre 500k req',
      'R$ 50 por mil req adicionais',
      'SSO/SAML',
      'IP allowlist com CIDR',
      'SLA contratual e suporte dedicado'
    ],
    limits: [
      'Adquirido apenas via contato comercial'
    ],
    planoBd: 'enterprise'
  }
];

export function getPlanBySlug(slug: PlanSlug): ApiPlan {
  return plans.find((plan) => plan.slug === slug) || plans[0];
}
