import { buildUrl } from './apiClient';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  usuario_id: string;
  cliente_id: string | null;
  role: string;
}

export interface PerfilTenant {
  cliente_id: string;
  nome: string;
  role: string;
  status: string;
  plano_nome: string;
}

export interface PerfilB2B {
  empresa: string;
  cnpj: string;
  telefone: string;
  cargo: string;
  segmento: string;
  objetivo_uso: string;
  site_empresa: string | null;
  tamanho_empresa: string | null;
  mensagem: string | null;
  aceite_termos_em: string | null;
  aceite_lgpd_em: string | null;
}

export interface PerfilResponse {
  id: string;
  email: string;
  nome: string;
  avatar_url: string | null;
  status: string;
  email_verificado: boolean;
  ultimo_login_em: string | null;
  criado_em: string;
  tenants: PerfilTenant[];
  perfil_b2b?: PerfilB2B | null;
}

async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(buildUrl(path), {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = (data as { detail?: { mensagem?: string } }).detail?.mensagem || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data as T;
}

async function get<T>(path: string, token: string): Promise<T> {
  const res = await fetch(buildUrl(path), {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = (data as { detail?: { mensagem?: string } }).detail?.mensagem || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data as T;
}

export interface CadastroB2BPayload {
  email: string;
  nome: string;
  senha: string;
  empresa: string;
  cnpj: string;
  telefone: string;
  cargo: string;
  segmento: string;
  objetivo_uso: string;
  aceite_termos: boolean;
  aceite_lgpd: boolean;
  site_empresa?: string;
  tamanho_empresa?: string;
  mensagem?: string;
}

export const authApi = {
  cadastro: (payload: CadastroB2BPayload) =>
    post<{ status: string; mensagem: string }>('/v1/auth/cadastro', payload),

  login: (email: string, senha: string) =>
    post<LoginResponse>('/v1/auth/login', { email, senha }),

  loginGoogle: (id_token: string) =>
    post<LoginResponse>('/v1/auth/google', { id_token }),

  verificarEmail: (token: string) =>
    post<{ status: string }>('/v1/auth/verificar-email', { token }),

  reenviarVerificacao: (email: string) =>
    post<{ status: string }>('/v1/auth/reenviar-verificacao', { email }),

  solicitarReset: (email: string) =>
    post<{ status: string }>('/v1/auth/reset/solicitar', { email }),

  confirmarReset: (token: string, nova_senha: string) =>
    post<{ status: string }>('/v1/auth/reset/confirmar', { token, nova_senha }),

  refresh: (refresh_token: string) =>
    post<{ access_token: string; refresh_token: string; token_type: string }>(
      '/v1/auth/refresh',
      { refresh_token }
    ),

  logout: (refresh_token: string) =>
    post<{ status: string }>('/v1/auth/logout', { refresh_token }),

  logoutTudo: (access_token: string) =>
    post<{ status: string }>('/v1/auth/logout-tudo', {}, access_token),

  perfil: (access_token: string) =>
    get<PerfilResponse>('/v1/me/perfil', access_token),
};
