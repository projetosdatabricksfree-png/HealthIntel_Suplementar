import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { ArrowLeft, Check, Copy, Eye, EyeOff, Key, Lock, Mail } from 'lucide-react';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';
import { authApi } from '../../services/authApi';
import { CNPJInput } from '../../components/forms/CNPJInput';
import { TelefoneInput } from '../../components/forms/TelefoneInput';
import { PasswordStrength } from '../../components/forms/PasswordStrength';
import { validarCNPJ, validarTelefoneBR, validarSenhaForte } from '../../utils/validators';

const SEGMENTOS = [
  { value: 'operadora', label: 'Operadora' },
  { value: 'corretora_administradora', label: 'Corretora / Administradora' },
  { value: 'healthtech', label: 'Healthtech' },
  { value: 'consultoria', label: 'Consultoria' },
  { value: 'hospital_prestador', label: 'Hospital / Prestador' },
  { value: 'escritorio_juridico', label: 'Escritório jurídico' },
  { value: 'bi_dados', label: 'BI / Dados' },
  { value: 'outro', label: 'Outro' },
];

const OBJETIVOS = [
  { value: 'testar_api', label: 'Testar a API' },
  { value: 'avaliar_dados_ans', label: 'Avaliar dados ANS' },
  { value: 'integrar_bi', label: 'Integrar com BI' },
  { value: 'pesquisa_regulatoria', label: 'Pesquisa regulatória' },
  { value: 'avaliacao_comercial', label: 'Avaliação comercial' },
];

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

type Mode = 'login' | 'cadastro' | 'reset_solicitar' | 'reset_enviado' | 'cadastro_enviado';

export function LoginPage() {
  const { login, loginWithGoogle, isAuthenticated, isLoading } = useAuth();
  const { success, error, warning } = useNotification();
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [nome, setNome] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [empresa, setEmpresa] = useState('');
  const [cnpj, setCnpj] = useState('');
  const [telefone, setTelefone] = useState('');
  const [cargo, setCargo] = useState('');
  const [segmento, setSegmento] = useState('');
  const [objetivoUso, setObjetivoUso] = useState('');
  const [aceiteTermos, setAceiteTermos] = useState(false);
  const [aceiteLgpd, setAceiteLgpd] = useState(false);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !senha) return;
    setSubmitting(true);
    try {
      await login(email.trim(), senha);
      success('Login realizado com sucesso.');
      navigate('/app');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Falha ao entrar. Verifique suas credenciais.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCadastro(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !nome.trim() || !senha) return;
    if (senha !== confirmarSenha) {
      error('As senhas não conferem.');
      return;
    }
    const senhaCheck = validarSenhaForte(senha);
    if (!senhaCheck.ok) {
      error(`Senha fraca: ${senhaCheck.motivo}`);
      return;
    }
    if (!empresa.trim() || !cargo.trim()) {
      error('Empresa e cargo são obrigatórios.');
      return;
    }
    if (!validarCNPJ(cnpj)) {
      error('CNPJ inválido. Verifique os dígitos.');
      return;
    }
    if (!validarTelefoneBR(telefone)) {
      error('Telefone inválido. Use DDD + número.');
      return;
    }
    if (!segmento || !objetivoUso) {
      error('Selecione o segmento e o objetivo de uso.');
      return;
    }
    if (!aceiteTermos || !aceiteLgpd) {
      error('É necessário aceitar os termos e a política de privacidade.');
      return;
    }
    setSubmitting(true);
    try {
      await authApi.cadastro({
        email: email.trim(),
        nome: nome.trim(),
        senha,
        empresa: empresa.trim(),
        cnpj,
        telefone,
        cargo: cargo.trim(),
        segmento,
        objetivo_uso: objetivoUso,
        aceite_termos: aceiteTermos,
        aceite_lgpd: aceiteLgpd,
      });
      setMode('cadastro_enviado');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Falha ao criar conta. Tente novamente.');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleReset(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    try {
      await authApi.solicitarReset(email.trim());
      setMode('reset_enviado');
    } catch {
      // sempre 200 no backend — nunca mostrar erro aqui
      setMode('reset_enviado');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleGoogleSuccess(credential: string) {
    setSubmitting(true);
    try {
      await loginWithGoogle(credential);
      success('Login com Google realizado.');
      navigate('/app');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Falha no login com Google.');
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
          <Link to="/" className="btn btn--ghost btn--sm">
            <ArrowLeft size={14} />
            Voltar ao site
          </Link>
        </div>

        <div className="login-form-wrap">
          {/* ---- Login ---- */}
          {mode === 'login' && (
            <>
              <h1 className="login-title">Entrar no HealthIntel</h1>
              <p className="login-sub">
                Acesse sua conta, API keys e área técnica.{' '}
                <button type="button" className="link-btn" onClick={() => setMode('cadastro')}>
                  Criar conta
                </button>
                .
              </p>

              <div className="social-stack">
                {GOOGLE_CLIENT_ID ? (
                  <GoogleLogin
                    onSuccess={(r) => r.credential && handleGoogleSuccess(r.credential)}
                    onError={() => error('Falha no login com Google.')}
                    text="signin_with"
                    shape="rectangular"
                    size="large"
                    width="380"
                  />
                ) : (
                  <button
                    type="button"
                    className="social-btn"
                    onClick={() => warning('Client ID Google não configurado.')}
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

              <div className="login-divider">ou por e-mail</div>

              <form onSubmit={handleLogin}>
                <div className="field">
                  <label className="field-label" htmlFor="email">E-mail</label>
                  <input
                    className="field-input"
                    id="email"
                    type="email"
                    placeholder="voce@empresa.com.br"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="field">
                  <label className="field-label" htmlFor="senha">
                    Senha
                    <button
                      type="button"
                      className="link-btn link-btn--right"
                      onClick={() => setMode('reset_solicitar')}
                    >
                      Esqueci minha senha
                    </button>
                  </label>
                  <div className="field-input-wrap">
                    <input
                      className="field-input"
                      id="senha"
                      type={mostrarSenha ? 'text' : 'password'}
                      placeholder="••••••••"
                      autoComplete="current-password"
                      value={senha}
                      onChange={(e) => setSenha(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="field-eye"
                      onClick={() => setMostrarSenha((v) => !v)}
                      aria-label={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
                    >
                      {mostrarSenha ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  className="btn btn--primary btn--lg login-submit"
                  disabled={submitting}
                >
                  <Mail size={16} />
                  {submitting ? 'Entrando…' : 'Entrar no portal'}
                </button>
              </form>

              <p className="login-foot">
                Não tem conta?{' '}
                <button type="button" className="link-btn" onClick={() => setMode('cadastro')}>
                  Criar conta grátis
                </button>
                {' · '}
                <Link to="/contato">Falar com comercial</Link>
              </p>
            </>
          )}

          {/* ---- Cadastro B2B ---- */}
          {mode === 'cadastro' && (
            <>
              <h1 className="login-title">Criar conta corporativa</h1>
              <p className="login-sub">
                Conta gratuita com 100 requisições/dia para avaliação técnica.{' '}
                <button type="button" className="link-btn" onClick={() => setMode('login')}>
                  Já tem conta? Entrar
                </button>
              </p>

              <form onSubmit={handleCadastro} className="form-b2b">
                <fieldset className="form-section">
                  <legend className="form-legend">Dados de acesso</legend>
                  <div className="fields-grid">
                    <div className="field">
                      <label className="field-label" htmlFor="c-nome">Nome completo *</label>
                      <input
                        className="field-input"
                        id="c-nome"
                        type="text"
                        autoComplete="name"
                        value={nome}
                        onChange={(e) => setNome(e.target.value)}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-email">E-mail corporativo *</label>
                      <input
                        className="field-input"
                        id="c-email"
                        type="email"
                        placeholder="voce@empresa.com.br"
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-senha">Senha (mín. 8) *</label>
                      <div className="field-input-wrap">
                        <input
                          className="field-input"
                          id="c-senha"
                          type={mostrarSenha ? 'text' : 'password'}
                          autoComplete="new-password"
                          value={senha}
                          onChange={(e) => setSenha(e.target.value)}
                          required
                          minLength={8}
                        />
                        <button
                          type="button"
                          className="field-eye"
                          onClick={() => setMostrarSenha((v) => !v)}
                          aria-label="Alternar visibilidade da senha"
                        >
                          {mostrarSenha ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                      <PasswordStrength senha={senha} />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-confirmar">Confirmar senha *</label>
                      <input
                        className="field-input"
                        id="c-confirmar"
                        type="password"
                        autoComplete="new-password"
                        value={confirmarSenha}
                        onChange={(e) => setConfirmarSenha(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </fieldset>

                <fieldset className="form-section">
                  <legend className="form-legend">Empresa</legend>
                  <div className="fields-grid">
                    <div className="field">
                      <label className="field-label" htmlFor="c-empresa">Nome da empresa *</label>
                      <input
                        className="field-input"
                        id="c-empresa"
                        type="text"
                        autoComplete="organization"
                        value={empresa}
                        onChange={(e) => setEmpresa(e.target.value)}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-cnpj">CNPJ *</label>
                      <CNPJInput
                        id="c-cnpj"
                        className="field-input"
                        value={cnpj}
                        onChange={setCnpj}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-telefone">Telefone / WhatsApp *</label>
                      <TelefoneInput
                        id="c-telefone"
                        className="field-input"
                        value={telefone}
                        onChange={setTelefone}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-cargo">Cargo *</label>
                      <input
                        className="field-input"
                        id="c-cargo"
                        type="text"
                        autoComplete="organization-title"
                        value={cargo}
                        onChange={(e) => setCargo(e.target.value)}
                        required
                      />
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-segmento">Segmento *</label>
                      <select
                        className="field-input"
                        id="c-segmento"
                        value={segmento}
                        onChange={(e) => setSegmento(e.target.value)}
                        required
                      >
                        <option value="">Selecione…</option>
                        {SEGMENTOS.map((s) => (
                          <option key={s.value} value={s.value}>
                            {s.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="field">
                      <label className="field-label" htmlFor="c-objetivo">Objetivo de uso *</label>
                      <select
                        className="field-input"
                        id="c-objetivo"
                        value={objetivoUso}
                        onChange={(e) => setObjetivoUso(e.target.value)}
                        required
                      >
                        <option value="">Selecione…</option>
                        {OBJETIVOS.map((o) => (
                          <option key={o.value} value={o.value}>
                            {o.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </fieldset>

                <div className="form-aceites">
                  <label className="aceite-row">
                    <input
                      type="checkbox"
                      checked={aceiteTermos}
                      onChange={(e) => setAceiteTermos(e.target.checked)}
                      required
                    />
                    <span>
                      Li e aceito os{' '}
                      <Link to="/seguranca" target="_blank" rel="noreferrer">
                        Termos de Uso
                      </Link>
                      .
                    </span>
                  </label>
                  <label className="aceite-row">
                    <input
                      type="checkbox"
                      checked={aceiteLgpd}
                      onChange={(e) => setAceiteLgpd(e.target.checked)}
                      required
                    />
                    <span>
                      Concordo com a{' '}
                      <Link to="/seguranca" target="_blank" rel="noreferrer">
                        Política de Privacidade e LGPD
                      </Link>
                      .
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  className="btn btn--primary btn--lg login-submit"
                  disabled={submitting}
                >
                  <Lock size={16} />
                  {submitting ? 'Criando conta…' : 'Criar conta grátis'}
                </button>
              </form>
            </>
          )}

          {/* ---- Cadastro enviado ---- */}
          {mode === 'cadastro_enviado' && (
            <div className="login-feedback">
              <div className="login-feedback__icon login-feedback__icon--ok">
                <Check size={24} />
              </div>
              <h2>Verifique seu e-mail</h2>
              <p>
                Enviamos um link de confirmação para <strong>{email}</strong>. Clique no link
                para ativar sua conta.
              </p>
              <p className="login-feedback__hint">
                Não recebeu?{' '}
                <button
                  type="button"
                  className="link-btn"
                  onClick={async () => {
                    await authApi.reenviarVerificacao(email);
                    success('E-mail reenviado.');
                  }}
                >
                  Reenviar
                </button>
              </p>
              <button
                type="button"
                className="btn btn--ghost btn--sm"
                onClick={() => setMode('login')}
              >
                Voltar ao login
              </button>
            </div>
          )}

          {/* ---- Reset — solicitar ---- */}
          {mode === 'reset_solicitar' && (
            <>
              <h1 className="login-title">Recuperar senha</h1>
              <p className="login-sub">
                Informe seu e-mail e enviaremos um link de redefinição.
              </p>
              <form onSubmit={handleReset}>
                <div className="field">
                  <label className="field-label" htmlFor="r-email">E-mail</label>
                  <input
                    className="field-input"
                    id="r-email"
                    type="email"
                    placeholder="voce@empresa.com.br"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn--primary btn--lg login-submit"
                  disabled={submitting}
                >
                  <Mail size={16} />
                  {submitting ? 'Enviando…' : 'Enviar link de redefinição'}
                </button>
              </form>
              <p className="login-foot">
                <button type="button" className="link-btn" onClick={() => setMode('login')}>
                  Voltar ao login
                </button>
              </p>
            </>
          )}

          {/* ---- Reset — confirmação de envio ---- */}
          {mode === 'reset_enviado' && (
            <div className="login-feedback">
              <div className="login-feedback__icon login-feedback__icon--ok">
                <Check size={24} />
              </div>
              <h2>Link enviado</h2>
              <p>
                Se o e-mail <strong>{email}</strong> estiver cadastrado, você receberá um link
                para redefinir sua senha em breve.
              </p>
              <button
                type="button"
                className="btn btn--ghost btn--sm"
                onClick={() => setMode('login')}
              >
                Voltar ao login
              </button>
            </div>
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
              Adquira um plano, faça login e a chave aparece na sua área de cliente, junto com
              logs, uso por endpoint e quickstart.
            </p>
          </div>

          <div className="login-quotes">
            <div className="login-quote">
              <span className="login-quote__icon"><Check size={12} strokeWidth={2.5} /></span>
              <span>Pipeline ANS gerenciado, sem você manter o ETL.</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon"><Check size={12} strokeWidth={2.5} /></span>
              <span>Todas as tabelas da ANS · TISS/SIB sob solicitação.</span>
            </div>
            <div className="login-quote">
              <span className="login-quote__icon"><Check size={12} strokeWidth={2.5} /></span>
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
