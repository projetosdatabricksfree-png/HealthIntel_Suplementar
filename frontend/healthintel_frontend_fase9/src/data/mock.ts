import type { UsagePoint, PortalUser } from '../types/domain';

export const demoUser: PortalUser = {
  nome: 'Diego Costa',
  email: 'cliente@healthintel.local',
  empresa: 'Cliente Demonstração',
  cargo: 'Analytics / BI',
  plano: 'Core API',
  apiKey: 'hi_local_dev_2026_api_key'
};

export const usageSeries: UsagePoint[] = [
  { dia: '01/05', requisicoes: 420, erros: 2, latenciaMs: 91 },
  { dia: '02/05', requisicoes: 620, erros: 4, latenciaMs: 87 },
  { dia: '03/05', requisicoes: 780, erros: 3, latenciaMs: 94 },
  { dia: '04/05', requisicoes: 940, erros: 6, latenciaMs: 102 },
  { dia: '05/05', requisicoes: 1210, erros: 5, latenciaMs: 89 },
  { dia: '06/05', requisicoes: 1110, erros: 2, latenciaMs: 85 },
  { dia: '07/05', requisicoes: 1350, erros: 4, latenciaMs: 92 }
];

export const sampleResponse = {
  dados: [
    {
      registro_ans: '000000',
      razao_social: 'Operadora Demonstração Saúde S.A.',
      uf: 'SP',
      modalidade: 'Medicina de Grupo',
      beneficiarios: 245120,
      score: 86.4,
      risco_regulatorio: 'baixo'
    }
  ],
  paginacao: {
    limite: 20,
    offset: 0,
    total_estimado: 1
  },
  metadados: {
    fonte: 'ANS',
    produto: 'HealthIntel Core ANS',
    ambiente: 'demo'
  }
};
