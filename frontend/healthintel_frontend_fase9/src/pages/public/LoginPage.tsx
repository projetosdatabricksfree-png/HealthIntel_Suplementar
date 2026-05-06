import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button } from '../../components/Button';
import { Card } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const allowedLocalKeys = new Set(['hi_local_dev_2026_api_key', 'hi_local_admin_2026_api_key']);

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const { success, error, warning } = useNotification();
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
        <p>
          Nesta versão, o portal usa e-mail + API key para habilitar testes. Em produção,
          substitua por autenticação com sessão segura e gestão real de usuários.
        </p>
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
          success('Login local realizado. Use o Live Tester para validar a API key na API real.');
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
