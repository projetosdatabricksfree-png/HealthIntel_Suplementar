import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AlertCircle, Check, Loader2 } from 'lucide-react';
import { authApi } from '../../services/authApi';

type Status = 'loading' | 'ok' | 'error';

export function VerificarEmailPage() {
  const [params] = useSearchParams();
  const [status, setStatus] = useState<Status>('loading');
  const [mensagem, setMensagem] = useState('');

  useEffect(() => {
    const token = params.get('token');
    if (!token) {
      setStatus('error');
      setMensagem('Link inválido. O token de verificação está ausente.');
      return;
    }
    authApi.verificarEmail(token)
      .then(() => setStatus('ok'))
      .catch((err) => {
        setStatus('error');
        setMensagem(err instanceof Error ? err.message : 'Link inválido ou expirado.');
      });
  }, [params]);

  return (
    <div className="verify-page">
      <div className="verify-card">
        <Link to="/" className="logo" style={{ marginBottom: '2rem', display: 'flex', gap: '8px', alignItems: 'center' }}>
          <img src="/logo-mark.png" alt="HealthIntel" width={28} height={28} />
          <span className="logo__word">healthintel</span>
        </Link>

        {status === 'loading' && (
          <>
            <Loader2 size={40} className="spin" style={{ color: 'var(--primary)', marginBottom: '1rem' }} />
            <h2>Verificando seu e-mail…</h2>
            <p className="verify-hint">
              Isso costuma levar 1 ou 2 segundos. Se demorar mais, recarregue a página ou
              cheque sua caixa de spam para reabrir o link de confirmação.
            </p>
          </>
        )}

        {status === 'ok' && (
          <>
            <div className="login-feedback__icon login-feedback__icon--ok" style={{ marginBottom: '1rem' }}>
              <Check size={28} />
            </div>
            <h2>E-mail confirmado!</h2>
            <p>Sua conta está ativa. Faça login para acessar o portal.</p>
            <Link to="/login" className="btn btn--primary" style={{ marginTop: '1.5rem' }}>
              Ir para o login
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="login-feedback__icon login-feedback__icon--err" style={{ marginBottom: '1rem' }}>
              <AlertCircle size={28} />
            </div>
            <h2>Link inválido</h2>
            <p>{mensagem || 'Este link de verificação é inválido ou já foi utilizado.'}</p>
            <Link to="/login" className="btn btn--ghost" style={{ marginTop: '1.5rem' }}>
              Voltar ao login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
