import { KeyRound, Terminal, Braces } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { ApiWidget } from './ApiWidget';

interface Step {
  n: string;
  Icon: LucideIcon;
  title: string;
  desc: string;
  chip: string;
}

const STEPS: Step[] = [
  {
    n: '01',
    Icon: KeyRound,
    title: 'Autentique a chamada',
    desc: 'Envie sua chave no header X-API-Key. Prefixo público hi_live_* (produção) ou hi_test_* (sandbox), uma chave por ambiente.',
    chip: 'X-API-Key',
  },
  {
    n: '02',
    Icon: Terminal,
    title: 'Consulte o endpoint',
    desc: 'GET no dataset, filtrando por registro_ans, competência ou UF. Paginação com page e page_size — sem baixar ZIP, sem layout fixo.',
    chip: 'GET /v1/{dataset}',
  },
  {
    n: '03',
    Icon: Braces,
    title: 'Receba o envelope',
    desc: 'Sempre { dados: [...], meta: {...} } em JSON, com total, página e competencia_referencia. Contrato estável, versionado em /v1.',
    chip: '{ dados, meta }',
  },
];

export function CustomerJourney() {
  return (
    <div className="journey">
      <div className="journey__steps">
        {STEPS.map((s) => (
          <div key={s.n} className="journey-step">
            <span className="journey-step__n mono">{s.n}</span>
            <span className="journey-step__icon">
              <s.Icon size={16} />
            </span>
            <p className="journey-step__t">{s.title}</p>
            <p className="journey-step__d">{s.desc}</p>
            <span className="journey-step__chip mono">{s.chip}</span>
          </div>
        ))}
      </div>
      <ApiWidget />
    </div>
  );
}
