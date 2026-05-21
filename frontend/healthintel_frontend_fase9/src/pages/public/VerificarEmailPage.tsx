import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AlertCircle, Check, Loader2, Mail } from 'lucide-react';
import { useNotification } from '../../components/NotificationProvider';
import { authApi } from '../../services/authApi';

type Status = 'loading' | 'ok' | 'error';

const COOLDOWN_SECONDS = 60;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function VerificarEmailPage() {
  const [params] = useSearchParams();
  const { success, error } = useNotification();
  const [status, setStatus] = useState<Status>('loading');
  const [mensagem, setMensagem] = useState('');

  const [resendEmail, setResendEmail] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [resendBusy, setResendBusy] = useState(false);
  const timerRef = useRef<number | null>(null);

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

  useEffect(() => {
    if (cooldown <= 0) {
      if (timerRef.current) window.clearInterval(timerRef.current);
      return;
    }
    timerRef.current = window.setInterval(() => {
      setCooldown((c) => (c > 0 ? c - 1 : 0));
    }, 1000);
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, [cooldown]);

  async function handleResend() {
    if (cooldown > 0 || resendBusy) return;
    if (!emailRegex.test(resendEmail.trim())) {
      error('Informe um e-mail válido para reenviar o link.');
      return;
    }
    setResendBusy(true);
    try {
      await authApi.reenviarVerificacao(resendEmail.trim());
      success('Se o e-mail estiver cadastrado, um novo link foi enviado.');
      setCooldown(COOLDOWN_SECONDS);
    } catch (err) {
      error(err instanceof Error ? err.message : 'Não foi possível reenviar agora.');
    } finally {
      setResendBusy(false);
    }
  }

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

            <div className="verify-resend">
              <input
                type="email"
                className="verify-resend__email"
                placeholder="seu@email.com"
                autoComplete="email"
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
                disabled={resendBusy || cooldown > 0}
              />
              <button
                type="button"
                className="btn btn--primary verify-resend__btn"
                onClick={handleResend}
                disabled={resendBusy || cooldown > 0 || !resendEmail.trim()}
              >
                <Mail size={14} />
                {resendBusy
                  ? 'Reenviando…'
                  : cooldown > 0
                    ? `Aguarde ${cooldown}s`
                    : 'Reenviar link de verificação'}
              </button>
              {cooldown > 0 && (
                <span className="verify-resend__status">
                  Novo envio liberado em {cooldown}s · cheque a caixa de spam.
                </span>
              )}
            </div>

            <Link to="/login" className="btn btn--ghost" style={{ marginTop: '1rem' }}>
              Voltar ao login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
