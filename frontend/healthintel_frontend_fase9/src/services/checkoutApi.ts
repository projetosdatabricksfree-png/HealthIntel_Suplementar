import { buildUrl } from './apiClient';

export type CheckoutPlano = 'sandbox' | 'piloto' | 'core';

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
