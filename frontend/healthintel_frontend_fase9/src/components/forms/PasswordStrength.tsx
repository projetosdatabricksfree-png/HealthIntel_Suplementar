import { useMemo } from 'react';

interface PasswordStrengthProps {
  senha: string;
}

interface Score {
  level: 0 | 1 | 2 | 3 | 4;
  label: string;
  tone: 'empty' | 'weak' | 'medium' | 'good' | 'strong';
  hint?: string;
}

function avaliarSenha(senha: string): Score {
  if (!senha) return { level: 0, label: 'Digite uma senha', tone: 'empty' };
  let pts = 0;
  if (senha.length >= 8) pts++;
  if (senha.length >= 12) pts++;
  if (/[A-Z]/.test(senha) && /[a-z]/.test(senha)) pts++;
  if (/\d/.test(senha)) pts++;
  if (/[^A-Za-z0-9]/.test(senha)) pts++;

  let hint: string | undefined;
  if (senha.length < 8) hint = 'Use ao menos 8 caracteres.';
  else if (!/\d/.test(senha)) hint = 'Adicione números.';
  else if (!/[A-Z]/.test(senha)) hint = 'Adicione letras maiúsculas.';
  else if (!/[^A-Za-z0-9]/.test(senha)) hint = 'Considere um símbolo para reforçar.';

  if (pts <= 1) return { level: 1, label: 'Muito fraca', tone: 'weak', hint };
  if (pts === 2) return { level: 2, label: 'Fraca', tone: 'weak', hint };
  if (pts === 3) return { level: 3, label: 'Média', tone: 'medium', hint };
  if (pts === 4) return { level: 4, label: 'Forte', tone: 'good', hint };
  return { level: 4, label: 'Muito forte', tone: 'strong' };
}

export function PasswordStrength({ senha }: PasswordStrengthProps) {
  const score = useMemo(() => avaliarSenha(senha), [senha]);
  return (
    <div className={`pwd-strength pwd-strength--${score.tone}`} aria-live="polite">
      <div className="pwd-strength__bars" aria-hidden="true">
        {[1, 2, 3, 4].map((i) => (
          <span key={i} className={`pwd-strength__bar${i <= score.level ? ' pwd-strength__bar--on' : ''}`} />
        ))}
      </div>
      <div className="pwd-strength__meta">
        <span className="pwd-strength__label">{score.label}</span>
        {score.hint && <span className="pwd-strength__hint">{score.hint}</span>}
      </div>
    </div>
  );
}
