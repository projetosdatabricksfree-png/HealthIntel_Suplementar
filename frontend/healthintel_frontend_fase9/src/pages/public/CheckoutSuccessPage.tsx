import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button, LinkButton } from '../../components/Button';
import { Card } from '../../components/Card';
import { useAuth } from '../../hooks/useAuth';
import { requestApi } from '../../services/apiClient';

type PageState = 'loading' | 'ok' | 'already_processed' | 'error';

export function CheckoutSuccessPage() {
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const sessionId = searchParams.get('session_id') || '';
  const planoBd = searchParams.get('plano_bd') || 'starter_local';

  const [pageState, setPageState] = useState<PageState>(sessionId ? 'loading' : 'error');
  const [apiKey, setApiKey] = useState('');
  const [email, setEmail] = useState('');
  const [copied, setCopied] = useState(false);
  const called = useRef(false);

  useEffect(() => {
    if (!sessionId || called.current) return;
    called.current = true;

    requestApi('/v1/checkout/confirmar', {
      method: 'POST',
      body: { session_id: sessionId, plano_bd: planoBd }
    }).then((result) => {
      if (result.ok) {
        const dados = (result.data as { dados?: { chave_api: string; email: string } }).dados;
        if (dados) {
          setApiKey(dados.chave_api);
          setEmail(dados.email);
          login(dados.email, dados.chave_api);
          setPageState('ok');
        } else {
          setPageState('error');
        }
      } else {
        const codigo = (result.data as { codigo?: string })?.codigo;
        setPageState(codigo === 'SESSAO_JA_PROCESSADA' ? 'already_processed' : 'error');
      }
    });
  }, [sessionId, planoBd, login]);

  function copyKey() {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  if (pageState === 'loading') {
    return (
      <section className="page section">
        <Card className="checkout-card">
          <p className="eyebrow">Aguarde</p>
          <h1>Confirmando pagamento...</h1>
          <p>Verificando o pagamento no Stripe. Não feche esta janela.</p>
        </Card>
      </section>
    );
  }

  if (pageState === 'already_processed') {
    return (
      <section className="page section">
        <Card className="checkout-card">
          <p className="eyebrow">Atenção</p>
          <h1>Sessão já processada</h1>
          <p>Esta sessão de pagamento já foi processada anteriormente. Sua chave API está disponível no portal.</p>
          <LinkButton to="/login">Ir para o login</LinkButton>
        </Card>
      </section>
    );
  }

  if (pageState === 'error') {
    return (
      <section className="page section">
        <Card className="checkout-card">
          <p className="eyebrow">Erro</p>
          <h1>Não foi possível confirmar o pagamento</h1>
          <p>
            Se o pagamento foi aprovado no cartão, entre em contato informando o e-mail usado:{' '}
            <Link to="/contato"><strong>Falar com suporte</strong></Link>
          </p>
          <LinkButton to="/precos" variant="secondary">Ver planos</LinkButton>
        </Card>
      </section>
    );
  }

  return (
    <section className="page section">
      <Card className="checkout-card">
        <p className="eyebrow">Pagamento confirmado</p>
        <h1>Sua API key está pronta</h1>
        <p>
          Esta chave é exibida <strong>uma única vez</strong>. Copie e guarde em local seguro.
        </p>
        <div className="api-key-reveal">
          <code className="api-key-code">{apiKey}</code>
          <Button onClick={copyKey} variant="secondary">
            {copied ? 'Copiado!' : 'Copiar'}
          </Button>
        </div>
        {email && <p className="checkout-email">Conta: <strong>{email}</strong></p>}
        <p className="checkout-hint">
          Use o header <code>X-API-Key: {apiKey.slice(0, 12)}...</code> em cada requisição.
        </p>
        <LinkButton to="/app">Ir para o portal</LinkButton>
      </Card>
    </section>
  );
}
