import type { ApiPlan, PlanSlug } from '../types/domain';
import { commercialLinks } from '../config/commercialLinks';

export const plans: ApiPlan[] = [
  {
    nome: 'PLATAFORMA',
    slug: 'free',
    preco: 'Sob contato',
    precoAnual: 'Sob contato',
    economiaAnual: null,
    descricao: 'Plataforma de acesso aos dados ANS com modelo B2B customizado.',
    limiteDiario: 'Sob negociação',
    keyLimit: 999,
    teamLimit: 999,
    features: [
      'Todos os datasets ANS',
      'API versionada com envelope JSON',
      'Autenticação X-API-Key',
      'Rate limit por plano',
      'Logs auditáveis'
    ],
    limits: [
      'Modelo comercial customizado por volume',
      'Negociado com time comercial'
    ],
    planoBd: 'free'
  }
];

export function getPlanBySlug(slug: PlanSlug): ApiPlan {
  return plans.find((plan) => plan.slug === slug) || plans[0];
}
