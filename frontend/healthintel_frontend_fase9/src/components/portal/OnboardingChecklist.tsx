import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Check, Circle, X } from 'lucide-react';

interface ChecklistStep {
  id: string;
  label: string;
  hint: string;
  href: string;
  ctaLabel: string;
  done: boolean;
}

interface OnboardingChecklistProps {
  hasApiKey: boolean;
  hasUsage: boolean;
}

const DISMISS_KEY = 'healthintel.onboarding.dismissed';

export function OnboardingChecklist({ hasApiKey, hasUsage }: OnboardingChecklistProps) {
  const [dismissed, setDismissed] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem(DISMISS_KEY) === '1';
  });

  const steps: ChecklistStep[] = [
    {
      id: 'verify',
      label: 'Verificar e-mail',
      hint: 'Conta confirmada e sessão ativa.',
      href: '/app/perfil',
      ctaLabel: 'Ver perfil',
      done: true,
    },
    {
      id: 'apikey',
      label: 'Gerar uma API key',
      hint: 'A chave fica visível só uma vez — copie e guarde.',
      href: '/app/api-keys',
      ctaLabel: 'Criar chave',
      done: hasApiKey,
    },
    {
      id: 'call',
      label: 'Fazer a primeira chamada',
      hint: 'Use o Explorer ou copie o curl da documentação.',
      href: '/app/explorer',
      ctaLabel: 'Abrir Explorer',
      done: hasUsage,
    },
    {
      id: 'usage',
      label: 'Conferir o consumo',
      hint: 'Veja requisições, erros e latência em /me/uso.',
      href: '/app/uso',
      ctaLabel: 'Ver uso',
      done: hasUsage,
    },
  ];

  const completed = steps.filter((s) => s.done).length;
  const total = steps.length;
  const allDone = completed === total;
  const next = steps.find((s) => !s.done);

  if (dismissed || allDone) return null;

  function handleDismiss() {
    window.localStorage.setItem(DISMISS_KEY, '1');
    setDismissed(true);
  }

  return (
    <section className="onboarding-card" aria-labelledby="onboarding-title">
      <header className="onboarding-card__head">
        <div>
          <p className="eyebrow">Próximos passos</p>
          <h2 id="onboarding-title">Sua jornada de integração</h2>
          <p className="onboarding-card__progress">
            <strong>{completed}</strong>/<strong>{total}</strong> concluídos
            {next && <> · próximo: <em>{next.label}</em></>}
          </p>
        </div>
        <button
          type="button"
          className="onboarding-card__close"
          aria-label="Dispensar checklist"
          onClick={handleDismiss}
        >
          <X size={16} />
        </button>
      </header>

      <ol className="onboarding-card__steps">
        {steps.map((step) => (
          <li
            key={step.id}
            className={`onboarding-step${step.done ? ' onboarding-step--done' : ''}`}
          >
            <span className="onboarding-step__icon" aria-hidden="true">
              {step.done ? <Check size={14} /> : <Circle size={14} />}
            </span>
            <div className="onboarding-step__body">
              <strong>{step.label}</strong>
              <small>{step.hint}</small>
            </div>
            {!step.done && (
              <Link to={step.href} className="onboarding-step__cta">
                {step.ctaLabel} <ArrowRight size={12} />
              </Link>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}
