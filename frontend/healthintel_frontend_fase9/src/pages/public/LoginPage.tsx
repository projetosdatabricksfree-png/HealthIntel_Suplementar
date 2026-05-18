import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { ArrowLeft, Check, Copy, Key } from 'lucide-react';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const allowedLocalKeys = new Set(['hi_local_dev_2026_api_key', 'hi_local_admin_2026_api_key']);
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export function LoginPage() {
  const { login, loginWithGoogle, isAuthenticated } = useAuth();
  const { success, error, warning } = useNotification();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [apiKey, setApiKey] = useState('');

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return (
    <div className="login-page">
      <section className="login-form-panel">
        <div className="login-top">
          <Link to="/" className="logo">
            <img src="/logo-mark.png" alt="HealthIntel" width={28} height={28} />
            <span className="logo__word">healthintel</span>
          </Link>
          <Link to="/" className="btn btn--ghost btn--sm">
            <ArrowLeft size={14} />
            Voltar ao site
          </Link>
        </div>

        <div className="login-form-wrap">
          <h1 className="login-title">Entrar no HealthIntel</h1>
          <p className="login-sub">
            Acesse sua conta, API keys e área técnica. Ainda não tem conta?{' '}
            <Link to="/#planos">Adquira um plano</Link>.
          </p>

          {GOOGLE_CLIENT_ID && (
            <div className="social-stack">
              <GoogleLogin
                onSuccess={(response) => {
                  if (response.credential) {
                    loginWithGoogle(response.credential);
                    success('Login com Google realizado.');
                    navigate('/app');
                  }
                }}
                onError={() => error('Falha no login com Google. Tente novamente.')}
                text="signin_with"
                shape="rectangular"
                size="large"
                width="380"
              />
            </div>
          )}

          <div className="login-divider">ou com API key</div>

          <form
            onSubmit={(event) => {
              event.preventDefault();
              const normalizedEmail = email.trim();
              const normalizedKey = apiKey.trim();
              if (!normalizedEmail || !normalizedKey) {
                error('Informe e-mail e API key.');
                return;
              }
              if (!emailRegex.test(normalizedEmail)) {
                error('Informe um e-mail válido.');
                return;
              }
              if (!allowedLocalKeys.has(normalizedKey)) {
                warning('Chave salva para teste. A API validará permissões reais no Live Tester.');
              }
              login(normalizedEmail, normalizedKey);
              success('Login realizado.');
            }}
          >
            <div className="field">
              <label className="field-label" htmlFor="email">E-mail corporativo</label>
              <input
                className="field-input"
                id="email"
                type="email"
                placeholder="voce@empresa.com.br"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="field">
              <label className="field-label" htmlFor="apikey">API key</label>
              <input
                className="field-input"
                id="apikey"
                type="text"
                placeholder="hi_live_••••••••"
                autoComplete="off"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
            <div className="field-row">
              <label className="field-check">
                <input type="checkbox" defaultChecked /> Manter conectado
              </label>
              <Link to="/contato">Esqueceu a chave?</Link>
            </div>
            <button type="submit" className="btn btn--primary btn--lg login-submit">
              Entrar no portal
            </button>
          </form>

          <p className="login-foot">
            Ainda não tem conta? <Link to="/#planos">Adquira um plano</Link>
            {' · '}Precisa de onboarding? <Link to="/contato">Falar com comercial</Link>
          </p>
        </div>

        <footer className="login-legal">
          <span>© 2026 HealthIntel · CNPJ 53.936.542/0001-37</span>
          <Link to="/seguranca">Termos</Link>
          <Link to="/seguranca">Privacidade</Link>
          <Link to="/seguranca">LGPD</Link>
        </footer>
      </section>

      <aside className="login-brand-panel">
        <div className="login-brand-grid" aria-hidden="true"></div>
        <div className="login-brand-inner">
          <span className="login-brand-eyebrow">
            <span className="pulse-dot pulse-dot--mint"></span>
            Área do cliente
          </span>
          <div>
            <h2 className="login-brand-title">
              Sua API key da ANS, pronta assim que você entrar.
            </h2>
            <p className="login-brand-sub">
              Adquira um plano, faça login com Google e a chave aparece na sua área de
              cliente, junto com logs, uso por endpoint e quickstart.
            </p>
          </div>

          <div className="login-quotes">
            <div className="login-quote">
              <span className="login-quote__icon">
                <Check size={12} strokeWidth={2.5} />
              </span>
              <span>Pipeline ANS gerenciado, sem você manter o ETL.</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon">
                <Check size={12} strokeWidth={2.5} />
              </span>
              <span>Todas as tabelas da ANS · TISS/SIB sob solicitação.</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon">
                <Check size={12} strokeWidth={2.5} />
              </span>
              <span>Audit log e versionamento /v1 com janela de deprecação.</span>
            </div>
          </div>

          <div className="login-brand-card">
            <div className="login-brand-card__head">
              <span className="login-brand-card__label">
                <Key size={11} />
                Sua API key
              </span>
              <span className="login-brand-card__pill">live · default</span>
            </div>
            <div className="login-brand-card__row">
              <code className="login-brand-card__key">hi_live_7Z3kP9rN••••••••••••47Fa</code>
              <button type="button" className="login-brand-card__btn">
                <Copy size={11} />
                Copiar
              </button>
            </div>
            <p className="login-brand-card__hint">
              <strong>X-API-Key</strong> · use no header HTTP de toda requisição.
            </p>
          </div>
        </div>
      </aside>
    </div>
  );
}
