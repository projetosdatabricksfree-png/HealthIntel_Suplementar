import { buildUrl } from './apiClient';
import { getAccessToken } from './storage';

export type CheckoutPlano = 'starter' | 'pro' | 'max';

export interface CheckoutSessaoResposta {
  dados?: {
    checkout_url?: string;
    session_id?: string;
    plano?: string;
  };
  detail?: {
    codigo?: string;
    mensagem?: string;
  };
}

export async function criarCheckoutSessao(plano: CheckoutPlano): Promise<string> {
  const response = await fetch(buildUrl('/v1/checkout/sessao'), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ plano })
  });

  const body = (await response.json().catch(() => ({}))) as CheckoutSessaoResposta;
  if (!response.ok) {
    throw new Error(
      body.detail?.mensagem || `Falha ao iniciar checkout (HTTP ${response.status}).`
    );
  }

  const checkoutUrl = body.dados?.checkout_url;
  if (!checkoutUrl) {
    throw new Error('Checkout criado sem URL de pagamento.');
  }
  return checkoutUrl;
}

export async function criarSessaoCustomerPortal(): Promise<string> {
  const at = getAccessToken();
  if (!at) throw new Error('Sessão expirada.');
  const response = await fetch(buildUrl('/v1/portal/billing/customer-portal'), {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${at}`,
    },
  });
  const body = (await response.json().catch(() => ({}))) as { dados?: { url?: string }; detail?: { mensagem?: string } };
  if (!response.ok) {
    throw new Error(body.detail?.mensagem || `Erro ao abrir portal de billing (HTTP ${response.status}).`);
  }
  const url = body.dados?.url;
  if (!url) throw new Error('Resposta sem URL do portal.');
  return url;
}
