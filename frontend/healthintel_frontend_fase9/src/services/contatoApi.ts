const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export interface LeadContatoPayload {
  nome: string;
  email: string;
  empresa: string;
  perfil: string;
  plano?: string;
  mensagem: string;
  origem?: string;
  honeypot?: string;
}

export interface LeadContatoResposta {
  ok: boolean;
  lead_id?: string;
  email_status?: 'enviado' | 'fila_local' | 'desabilitado';
  detalhe?: string;
}

export async function enviarLead(payload: LeadContatoPayload): Promise<LeadContatoResposta> {
  const url = `${API_BASE.replace(/\/$/, '')}/v1/contato/leads`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  let body: LeadContatoResposta;
  try {
    body = (await response.json()) as LeadContatoResposta;
  } catch {
    body = { ok: false, detalhe: 'Resposta inválida do servidor.' };
  }

  if (!response.ok) {
    return { ok: false, detalhe: body.detalhe || `HTTP ${response.status}` };
  }
  return body;
}
