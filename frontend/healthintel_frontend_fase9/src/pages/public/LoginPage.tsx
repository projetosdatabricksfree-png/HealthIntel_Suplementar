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

          <div className="social-stack">
            {GOOGLE_CLIENT_ID ? (
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
            ) : (
              <button
                type="button"
                className="social-btn"
                onClick={() => warning('Login com Google disponível após configurar o Client ID. Entre com e-mail e API key.')}
              >
                <span className="social-btn__icon">
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
                    <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                    <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
                    <path d="M3.964 10.707A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.707V4.961H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.039l3.007-2.332z" fill="#FBBC05"/>
                    <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.961L3.964 6.293C4.672 4.166 6.656 3.58 9 3.58z" fill="#EA4335"/>
                  </svg>
                </span>
                <span className="social-btn__label">Entrar com Google</span>
              </button>
            )}
          </div>

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
