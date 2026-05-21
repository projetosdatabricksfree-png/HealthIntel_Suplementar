import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Lock } from 'lucide-react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';
import { canAccessFeature, getCurrentPlan } from '../../data/planRules';
import { buildUrl } from '../../services/apiClient';
import { getAccessToken } from '../../services/storage';
import type { TeamMember } from '../../types/domain';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const ROLES = ['owner', 'admin', 'developer', 'billing', 'viewer'] as const;

async function apiFetch<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const at = getAccessToken();
  const res = await fetch(buildUrl(path), {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(at ? { Authorization: `Bearer ${at}` } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = (json as { detail?: { mensagem?: string } }).detail?.mensagem || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return json as T;
}

export function TeamPage() {
  const { user } = useAuth();
  const { success, error } = useNotification();
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<typeof ROLES[number]>('viewer');
  const [inviting, setInviting] = useState(false);
  const currentPlan = getCurrentPlan(user?.tenant_ativo?.plano_nome);
  const podeAcessar = canAccessFeature(user?.tenant_ativo?.plano_nome, 'team');

  const loadMembers = useCallback(async () => {
    if (!podeAcessar) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await apiFetch<{ dados: TeamMember[] }>('/v1/portal/team');
      setMembers(data.dados);
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao carregar equipe.');
    } finally {
      setLoading(false);
    }
  }, [error, podeAcessar]);

  useEffect(() => { void loadMembers(); }, [loadMembers]);

  if (!podeAcessar) {
    return (
      <div className="plan-gate">
        <Lock size={32} />
        <h2>Disponível a partir do plano PRO</h2>
        <p>Seu plano atual é {currentPlan.nome}. Colabore com sua equipe, convide membros e defina papéis a partir do PRO.</p>
        <Link to="/app/billing" className="btn btn--primary">Ver planos</Link>
      </div>
    );
  }

  async function invite() {
    if (!emailRegex.test(email.trim())) { error('Informe um e-mail válido.'); return; }
    setInviting(true);
    try {
      await apiFetch('/v1/portal/team/convite', 'POST', { email: email.trim(), role });
      setEmail('');
      setShowInvite(false);
      await loadMembers();
      success('Convite enviado. O membro aparecerá na lista após aceitar.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao convidar membro.');
    } finally {
      setInviting(false);
    }
  }

  async function changeRole(userId: string, newRole: string) {
    try {
      await apiFetch(`/v1/portal/team/${userId}`, 'PATCH', { role: newRole });
      await loadMembers();
      success('Papel atualizado.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao alterar papel.');
    }
  }

  async function removeMember(userId: string) {
    try {
      await apiFetch(`/v1/portal/team/${userId}`, 'DELETE');
      await loadMembers();
      success('Membro removido.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao remover membro.');
    }
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Equipe</p>
          <h1>Usuários e permissões</h1>
          <p>Gerencie membros e papéis da sua organização.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Membros" description="Usuários com acesso ao portal desta organização." />
        <div className="table-wrap">
          <table>
            <thead><tr><th>Nome</th><th>E-mail</th><th>Papel</th><th>Status</th><th>Último login</th><th>Ações</th></tr></thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} style={{ color: 'var(--muted)', textAlign: 'center', padding: '1rem' }}>Carregando…</td></tr>
              ) : members.length === 0 ? (
                <tr><td colSpan={6} style={{ color: 'var(--muted)', textAlign: 'center', padding: '1rem' }}>Nenhum membro encontrado.</td></tr>
              ) : members.map((m) => (
                <tr key={m.id}>
                  <td>{m.nome}</td>
                  <td>{m.email}</td>
                  <td>
                    {m.role === 'owner' ? (
                      <span>{m.role}</span>
                    ) : (
                      <select value={m.role} onChange={(e) => void changeRole(m.id, e.target.value)}>
                        {ROLES.filter(r => r !== 'owner').map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    )}
                  </td>
                  <td>{m.status}</td>
                  <td>{m.ultimo_login_em ? new Date(m.ultimo_login_em).toLocaleDateString('pt-BR') : '—'}</td>
                  <td>
                    {m.role !== 'owner' && m.id !== user?.id && (
                      <Button variant="danger" onClick={() => void removeMember(m.id)}>Remover</Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="button-row">
          <Button onClick={() => setShowInvite(true)}>Convidar membro</Button>
          <Button variant="secondary" onClick={() => void loadMembers()}>Atualizar</Button>
        </div>
      </Card>

      {showInvite && (
        <Card className="modal-card">
          <CardHeader title="Convidar membro" description="Um e-mail de convite será enviado com link de acesso." />
          <div className="form-grid single">
            <label>E-mail<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>
              Papel
              <select value={role} onChange={(event) => setRole(event.target.value as typeof ROLES[number])}>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </label>
            <div className="button-row">
              <Button onClick={() => void invite()} disabled={inviting}>{inviting ? 'Enviando…' : 'Enviar convite'}</Button>
              <Button variant="secondary" onClick={() => setShowInvite(false)}>Cancelar</Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
