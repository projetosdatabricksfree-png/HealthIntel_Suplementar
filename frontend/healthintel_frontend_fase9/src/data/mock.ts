import type { UsagePoint } from '../types/domain';

// ATENÇÃO: este arquivo contém apenas dados de demonstração para fallback em
// ambientes de desenvolvimento/homologação. Nunca deve ser usado em produção.
// O fallback é gated por VITE_ENABLE_DEMO_FALLBACK + import.meta.env.MODE !== 'production'
// em src/services/apiClient.ts. Em produção, falhas de rede propagam normalmente
// (sem maquiar erro como sucesso).
if (typeof window !== 'undefined' && import.meta.env.MODE === 'production' &&
    String(import.meta.env.VITE_ENABLE_DEMO_FALLBACK ?? 'false') === 'true') {
  console.error(
    '[HealthIntel] CRÍTICO: VITE_ENABLE_DEMO_FALLBACK=true em build de produção. ' +
      'Mocks comerciais não devem ser exibidos. Verifique seu .env de build.'
  );
}

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
