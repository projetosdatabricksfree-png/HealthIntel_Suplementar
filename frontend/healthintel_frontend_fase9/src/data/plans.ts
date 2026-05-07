import type { ApiPlan } from '../types/domain';

const STRIPE_PAYMENT_LINK_SANDBOX = String(
  import.meta.env.VITE_STRIPE_PAYMENT_LINK_SANDBOX ?? ''
).trim();

export const plans: ApiPlan[] = [
  {
    nome: 'Sandbox Técnico',
    slug: 'sandbox',
    preco: 'R$ 99,99/mês',
    descricao: 'Teste de integração para validar autenticação, formato das respostas e consumo inicial.',
    features: [
      '100 requisições por mês',
      '1 API key',
      'Endpoints Core selecionados',
      'Snapshot histórico controlado',
      'Exemplos cURL e Swagger'
    ],
    limits: [
      'Sem uso comercial',
      'Sem SLA',
      'Sem suporte dedicado'
    ],
    stripePaymentLink: STRIPE_PAYMENT_LINK_SANDBOX,
    planoBd: 'starter_local'
  },
  {
    nome: 'Piloto Assistido',
    slug: 'piloto',
    preco: 'R$ 2.500',
    descricao: 'Validação técnica e comercial com acompanhamento para empresas do setor.',
    features: [
      '1 API key',
      'Endpoints Core',
      'Swagger e Postman',
      'Onboarding técnico',
      'Suporte assíncrono'
    ],
    limits: [
      'Sem extração integral',
      'Limite controlado de requisições',
      'Sem SLA enterprise'
    ]
  },
  {
    nome: 'Core API',
    slug: 'core',
    preco: 'R$ 4.900/mês',
    descricao: 'Produto principal para consumo recorrente de dados ANS tratados via API.',
    destaque: true,
    features: [
      'Operadoras 360',
      'Beneficiários',
      'Rankings',
      'Score',
      'Financeiro',
      'Regulatório',
      'Mercado por município',
      'CNES agregado'
    ],
    limits: [
      '1 a 3 API keys',
      'Rate limit por plano',
      'Logs de consumo'
    ]
  },
  {
    nome: 'Core Pro',
    slug: 'core',
    preco: 'R$ 9.900/mês',
    descricao: 'Para times que precisam acelerar integração, consumo analítico e operação interna.',
    features: [
      'Tudo do Core API',
      'Maior volume de requisições',
      'Mais API keys',
      'Apoio técnico de integração',
      'Exemplos para Power BI e notebooks',
      'Onboarding avançado',
      'Revisão mensal de consumo'
    ],
    limits: [
      'Sem acesso a camadas internas',
      'Uso conforme contrato',
      'Escopo técnico combinado'
    ]
  },
  {
    nome: 'Enterprise',
    slug: 'enterprise',
    preco: 'Sob contrato',
    descricao: 'Ambiente dedicado, histórico ampliado e datasets adicionais.',
    features: [
      'Histórico sob demanda',
      'Ambiente dedicado',
      'SLA customizado',
      'Módulos avançados sob contrato',
      'Integrações específicas',
      'Suporte prioritário'
    ],
    limits: [
      'Contrato mínimo',
      'Política anti redistribuição',
      'Auditoria de uso'
    ]
  }
];
