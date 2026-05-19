import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Check, Eye, EyeOff, Lock, Shield } from 'lucide-react';
import { useNotification } from '../../components/NotificationProvider';
import { authApi } from '../../services/authApi';

export function ResetSenhaPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { error } = useNotification();

  const token = params.get('token') || '';
  const [senha, setSenha] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const [mostrar, setMostrar] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (senha !== confirmar) {
      error('As senhas não conferem.');
      return;
    }
    if (senha.length < 8) {
      error('A senha deve ter ao menos 8 caracteres.');
      return;
    }
    setSubmitting(true);
    try {
      await authApi.confirmarReset(token, senha);
      setDone(true);
    } catch (err) {
      error(err instanceof Error ? err.message : 'Link inválido ou expirado.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-form-panel">
        <div className="login-top">
          <Link to="/" className="logo">
            <img src="/logo-mark.png" alt="HealthIntel" width={28} height={28} />
            <span className="logo__word">healthintel</span>
          </Link>
          <Link to="/login" className="btn btn--ghost btn--sm">
            <ArrowLeft size={14} />
            Voltar ao login
          </Link>
        </div>

        <div className="login-form-wrap">
          {!token ? (
            <>
              <div className="login-feedback__icon login-feedback__icon--err">
                <AlertCircle size={28} />
              </div>
              <h1 className="login-title">Link inválido</h1>
              <p className="login-sub">O link de redefinição está incompleto ou expirado. Solicite um novo link de redefinição.</p>
              <Link to="/login" className="btn btn--outline btn--lg login-submit">
                Voltar ao login
              </Link>
            </>
          ) : done ? (
            <>
              <div className="login-feedback__icon login-feedback__icon--ok">
                <Check size={28} />
              </div>
              <h1 className="login-title">Senha redefinida!</h1>
              <p className="login-sub">Sua senha foi atualizada com sucesso. Faça login com a nova senha.</p>
              <button
                type="button"
                className="btn btn--primary btn--lg login-submit"
                onClick={() => navigate('/login')}
              >
                Ir para o login
              </button>
            </>
          ) : (
            <>
              <h1 className="login-title">Nova senha</h1>
              <p className="login-sub">Escolha uma senha forte com ao menos 8 caracteres.</p>
              <form onSubmit={handleSubmit}>
                <div className="field">
                  <label className="field-label" htmlFor="nova-senha">Nova senha</label>
                  <div className="field-input-wrap">
                    <input
                      className="field-input"
                      id="nova-senha"
                      type={mostrar ? 'text' : 'password'}
                      placeholder="••••••••"
                      autoComplete="new-password"
                      value={senha}
                      onChange={(e) => setSenha(e.target.value)}
                      required
                      minLength={8}
                    />
                    <button
                      type="button"
                      className="field-eye"
                      onClick={() => setMostrar((v) => !v)}
                      aria-label="Alternar visibilidade"
                    >
                      {mostrar ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
                <div className="field">
                  <label className="field-label" htmlFor="confirmar-senha">Confirmar senha</label>
                  <input
                    className="field-input"
                    id="confirmar-senha"
                    type="password"
                    placeholder="••••••••"
                    autoComplete="new-password"
                    value={confirmar}
                    onChange={(e) => setConfirmar(e.target.value)}
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn--primary btn--lg login-submit"
                  disabled={submitting}
                >
                  {submitting ? 'Salvando…' : 'Salvar nova senha'}
                </button>
              </form>
            </>
          )}
        </div>

        <footer className="login-legal">
          <span>© 2026 HealthIntel · CNPJ 53.936.542/0001-37</span>
          <Link to="/seguranca">Termos</Link>
          <Link to="/seguranca">Privacidade</Link>
          <Link to="/seguranca">LGPD</Link>
        </footer>
      </section>

      <aside className="login-brand-panel">
        <div className="login-brand-grid" aria-hidden="true" />
        <div className="login-brand-inner">
          <span className="login-brand-eyebrow">
            <span className="pulse-dot pulse-dot--mint" />
            Segurança · Acesso protegido
          </span>
          <div>
            <h2 className="login-brand-title">
              Proteção de conta em todas as camadas
            </h2>
            <p className="login-brand-sub">
              Tokens de redefinição de uso único, expiração automática e senhas com bcrypt — sua conta está segura.
            </p>
          </div>
          <div className="login-quotes">
            <div className="login-quote">
              <span className="login-quote__icon"><Lock size={12} strokeWidth={2.5} /></span>
              <span>Link de redefinição expira em 2 horas</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon"><Shield size={12} strokeWidth={2.5} /></span>
              <span>Senhas protegidas com bcrypt rounds=12</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon"><Check size={12} strokeWidth={2.5} /></span>
              <span>Sessões ativas são revogadas ao redefinir</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon"><Check size={12} strokeWidth={2.5} /></span>
              <span>Máximo 5 tentativas antes de bloqueio temporário</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
