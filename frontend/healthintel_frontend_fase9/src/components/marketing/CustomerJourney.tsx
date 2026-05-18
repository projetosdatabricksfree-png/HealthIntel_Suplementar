import { useState } from 'react';
import { Zap, ShieldCheck, Key, Globe, Activity, FileText, Database, Terminal, ArrowRight, Eye, EyeOff, Copy, Check } from 'lucide-react';

const STEPS = [
  {
    n: '01',
    Icon: Zap,
    title: 'Adquira o plano',
    desc: 'Escolha FREE, STARTER, PRO ou MAX. Checkout direto no Stripe com cartão ou Pix.',
    chip: 'via Stripe',
  },
  {
    n: '02',
    Icon: ShieldCheck,
    title: 'Entre com Google',
    desc: 'Login único via Google Workspace ou Gmail. Sem criar mais uma senha corporativa.',
    chip: 'OAuth Google',
  },
  {
    n: '03',
    Icon: Key,
    title: 'Use sua API key',
    desc: 'A chave aparece na área do cliente assim que o pagamento é confirmado.',
    chip: 'X-API-Key',
  },
];

const DEMO_KEY = 'hi_live_7Z3kP9rN2vQa6mLx8Hb4dEc1uYt5oWfA47Fa';
const MASKED_KEY = 'hi_live_7Z3kP9rN' + '•'.repeat(20) + '47Fa';

function CustomerDashboardMock() {
  const [copied, setCopied] = useState(false);
  const [revealed, setRevealed] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(DEMO_KEY).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  }

  const curlCmd = `curl -H "X-API-Key: ${revealed ? '$HI_KEY' : '•••••'}" \\\n  "https://api.healthintel.com.br/v1/operadoras?per_page=10"`;

  return (
    <div className="dash">
      <div className="dash__chrome">
        <div className="api-widget__dots"><span /><span /><span /></div>
        <div className="dash__url">
          <Globe size={11} />
          <span className="mono">healthintel.com.br/app</span>
        </div>
        <span className="dash__env mono">Produção</span>
      </div>
      <div className="dash__body">
        <aside className="dash__nav">
          <p className="dash__nav-section">Conta</p>
          <span className="dash__nav-item is-active"><Key size={14} /> Chaves de API</span>
          <span className="dash__nav-item"><Activity size={14} /> Uso &amp; rate limit</span>
          <span className="dash__nav-item"><FileText size={14} /> Logs</span>
          <span className="dash__nav-item"><Database size={14} /> Datasets</span>
          <span className="dash__nav-item"><Terminal size={14} /> Documentação</span>
          <div className="dash__user">
            <span className="dash__avatar">A</span>
            <div>
              <p className="dash__user-name">Alex Pereira</p>
              <p className="dash__user-mail mono">alex@empresa.com.br</p>
            </div>
          </div>
        </aside>
        <main className="dash__main">
          <div className="dash__topbar">
            <div>
              <p className="dash__greeting">Olá, Alex</p>
              <p className="dash__sub">Bem-vindo de volta à HealthIntel.</p>
            </div>
            <div className="dash__plan-pill">
              <Check size={12} />
              Plano <strong>PRO</strong> · ativo
            </div>
          </div>
          <div className="dash__cards">
            <div className="dash__card dash__card--key">
              <div className="dash__card-head">
                <span className="dash__card-label"><Key size={12} /> Sua API key</span>
                <span className="dash__card-tag mono">live · default</span>
              </div>
              <div className="dash__key-row">
                <code className="mono dash__key">{revealed ? DEMO_KEY : MASKED_KEY}</code>
                <button
                  type="button"
                  className="dash__key-btn"
                  onClick={() => setRevealed((v) => !v)}
                  title={revealed ? 'Esconder' : 'Revelar'}
                >
                  {revealed ? <EyeOff size={13} /> : <Eye size={13} />}
                </button>
                <button
                  type="button"
                  className="dash__key-btn dash__key-btn--copy"
                  onClick={handleCopy}
                >
                  <Copy size={13} />
                  <span>{copied ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
              <p className="dash__card-hint mono">Use no header: <strong>X-API-Key: ••••</strong></p>
            </div>
            <div className="dash__metrics">
              <div className="dash__metric">
                <p className="dash__metric-label">Requisições hoje</p>
                <p className="dash__metric-value">47.328 <span className="dash__metric-unit">/ 150 mil</span></p>
                <div className="dash__bar"><div className="dash__bar-fill" style={{ width: '31%' }} /></div>
              </div>
              <div className="dash__metric">
                <p className="dash__metric-label">Latência p50</p>
                <p className="dash__metric-value">62<span className="dash__metric-unit">ms</span></p>
                <p className="dash__metric-trend dash__metric-trend--ok"><Check size={11} /> dentro do SLA</p>
              </div>
              <div className="dash__metric">
                <p className="dash__metric-label">Erros 24h</p>
                <p className="dash__metric-value">0</p>
                <p className="dash__metric-trend">últimos 7d</p>
              </div>
            </div>
          </div>
          <div className="dash__quickstart">
            <div className="dash__quickstart-head">
              <span className="eyebrow eyebrow--muted">Próximo passo</span>
              <p className="dash__quickstart-t">Faça sua primeira requisição</p>
            </div>
            <pre className="dash__quickstart-code mono">{curlCmd}</pre>
          </div>
        </main>
      </div>
    </div>
  );
}

export function CustomerJourney() {
  return (
    <div className="journey">
      <div className="journey__steps">
        {STEPS.map((s, i) => (
          <div key={s.n} className="journey-step">
            <span className="journey-step__n mono">{s.n}</span>
            <span className="journey-step__icon"><s.Icon size={16} /></span>
            <p className="journey-step__t">{s.title}</p>
            <p className="journey-step__d">{s.desc}</p>
            <span className="journey-step__chip mono">{s.chip}</span>
            {i < STEPS.length - 1 && (
              <span className="journey-step__arrow" aria-hidden="true">
                <ArrowRight size={16} />
              </span>
            )}
          </div>
        ))}
      </div>
      <CustomerDashboardMock />
    </div>
  );
}
