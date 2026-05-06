import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, addTeamInvite, getTeamInvites, updateTeamInvites, type TeamInvite } from '../../services/localPortalStore';
import { useAuth } from '../../hooks/useAuth';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function TeamPage() {
  const { user } = useAuth();
  const { success, error, info } = useNotification();
  const [showInvite, setShowInvite] = useState(false);
  const [email, setEmail] = useState('');
  const [papel, setPapel] = useState<TeamInvite['papel']>('Leitor');
  const [invites, setInvites] = useState(getTeamInvites());

  function invite() {
    if (!emailRegex.test(email.trim())) {
      error('Informe um e-mail válido.');
      return;
    }
    const next = addTeamInvite({ email: email.trim(), papel });
    setInvites((current) => [next, ...current]);
    addAuditEvent({
      tipo: 'membro_convidado',
      usuario: user?.email || 'portal_local',
      detalhe: `Convite local enviado para ${email.trim()} com papel ${papel}.`,
      status: 'sucesso'
    });
    setEmail('');
    setShowInvite(false);
    success('Convite salvo localmente para homologação.');
  }

  function setInviteStatus(id: string, status: TeamInvite['status']) {
    const next = invites.map((inviteItem) => inviteItem.id === id ? { ...inviteItem, status } : inviteItem);
    setInvites(next);
    updateTeamInvites(next);
    addAuditEvent({
      tipo: status === 'cancelado' ? 'convite_cancelado' : 'membro_removido',
      usuario: user?.email || 'portal_local',
      detalhe: `Registro ${id} atualizado para ${status}.`,
      status: 'sucesso'
    });
    success('Registro de equipe atualizado localmente.');
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Equipe</p>
          <h1>Usuários e permissões</h1>
          <p>Tela preparada para multiusuário por cliente.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Membros" description="Em produção, cada usuário deve ter papel e trilha de auditoria." />
        <div className="table-wrap">
          <table>
            <thead><tr><th>Nome</th><th>E-mail</th><th>Papel</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td>Diego Costa</td><td>cliente@healthintel.local</td><td>Owner</td><td>Ativo</td></tr>
              <tr><td>Analista BI</td><td>bi@empresa.com.br</td><td>Leitor</td><td>Convite pendente</td></tr>
              {invites.map((inviteItem) => (
                <tr key={inviteItem.id}>
                  <td>Convite local</td>
                  <td>{inviteItem.email}</td>
                  <td>{inviteItem.papel}</td>
                  <td>{inviteItem.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="button-row">
          <Button onClick={() => setShowInvite(true)}>Convidar membro</Button>
          <Button variant="secondary" onClick={() => info('Papéis disponíveis nesta homologação: Owner, Admin, Leitor e Billing.')}>Configurar papéis</Button>
          {invites[0] && <Button variant="secondary" onClick={() => setInviteStatus(invites[0].id, 'cancelado')}>Cancelar convite</Button>}
          {invites[0] && <Button variant="danger" onClick={() => setInviteStatus(invites[0].id, 'removido')}>Remover membro local/demo</Button>}
        </div>
      </Card>

      {showInvite && (
        <Card className="modal-card">
          <CardHeader title="Convidar membro" description="Convite local para homologação. Envio real depende de backend de usuários." />
          <div className="form-grid single">
            <label>E-mail<input value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>
              Papel
              <select value={papel} onChange={(event) => setPapel(event.target.value as TeamInvite['papel'])}>
                <option>Owner</option>
                <option>Admin</option>
                <option>Leitor</option>
                <option>Billing</option>
              </select>
            </label>
            <div className="button-row">
              <Button onClick={invite}>Salvar convite local</Button>
              <Button variant="secondary" onClick={() => setShowInvite(false)}>Cancelar</Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
