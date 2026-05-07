import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { Button } from '../../components/Button';
import { Card } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const allowedLocalKeys = new Set(['hi_local_dev_2026_api_key', 'hi_local_admin_2026_api_key']);
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export function LoginPage() {
  const { login, loginWithGoogle, isAuthenticated } = useAuth();
  const { success, error, warning } = useNotification();
  const navigate = useNavigate();
  const [email, setEmail] = useState('cliente@healthintel.local');
  const [apiKey, setApiKey] = useState('hi_local_dev_2026_api_key');

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return (
    <section className="login-page">
      <Card className="login-card">
        <p className="eyebrow">Portal do cliente</p>
        <h1>Entrar no HealthIntel</h1>

        {GOOGLE_CLIENT_ID && (
          <div className="google-login-wrapper">
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
              width="100%"
            />
            <div className="login-divider"><span>ou entre com API key</span></div>
          </div>
        )}

        <form onSubmit={(event) => {
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
        }}>
          <label>
            E-mail
            <input value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label>
            API key
            <input value={apiKey} onChange={(event) => setApiKey(event.target.value)} />
          </label>
          <Button type="submit">Entrar no portal</Button>
        </form>
      </Card>
    </section>
  );
}
