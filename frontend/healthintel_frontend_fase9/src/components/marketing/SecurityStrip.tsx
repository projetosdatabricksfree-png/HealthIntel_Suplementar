import { Key, Gauge, Scroll, GitBranch, Shield } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface SecurityItem {
  Icon: LucideIcon;
  t: string;
  d: string;
}

const SECURITY: SecurityItem[] = [
  { Icon: Key, t: 'X-API-Key', d: 'Autenticação por header, escopo por plano.' },
  { Icon: Gauge, t: 'Rate limit', d: 'Limites previsíveis por plano e endpoint.' },
  { Icon: Scroll, t: 'Logs por chave', d: 'Trilha auditável de consumo, exportável.' },
  { Icon: GitBranch, t: 'Versionamento', d: 'Prefixo /v1 e janela de deprecação anunciada.' },
  { Icon: Shield, t: 'LGPD', d: 'Tratamento sobre dados públicos da ANS.' },
];

export function SecurityStrip() {
  return (
    <div className="security-grid">
      {SECURITY.map((s) => (
        <div key={s.t} className="security-card">
          <span className="icon-tile">
            <s.Icon size={16} />
          </span>
          <p className="security-card__t">{s.t}</p>
          <p className="security-card__d">{s.d}</p>
        </div>
      ))}
    </div>
  );
}
