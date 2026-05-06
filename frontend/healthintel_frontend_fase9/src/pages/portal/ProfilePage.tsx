import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';
import { addAuditEvent } from '../../services/localPortalStore';

export function ProfilePage() {
  const { user, updateUser } = useAuth();
  const { success, error } = useNotification();
  const [nome, setNome] = useState(user?.nome || '');
  const [empresa, setEmpresa] = useState(user?.empresa || '');
  const [cargo, setCargo] = useState(user?.cargo || '');

  function save() {
    if (!nome.trim() || !empresa.trim() || !cargo.trim()) {
      error('Informe nome, empresa e cargo.');
      return;
    }
    if (!user) return;
    updateUser({ ...user, nome: nome.trim(), empresa: empresa.trim(), cargo: cargo.trim() });
    addAuditEvent({
      tipo: 'perfil_salvo',
      usuario: user.email,
      detalhe: 'Perfil salvo localmente.',
      status: 'sucesso'
    });
    success('Perfil salvo localmente e topbar atualizada.');
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Perfil</p>
          <h1>Dados da conta</h1>
          <p>Perfil completo do cliente para operação comercial e suporte.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Informações principais" description="Dados salvos localmente nesta versão." />
        <div className="form-grid">
          <label>Nome<input value={nome} onChange={(event) => setNome(event.target.value)} /></label>
          <label>E-mail<input value={user?.email || ''} disabled /></label>
          <label>Empresa<input value={empresa} onChange={(event) => setEmpresa(event.target.value)} /></label>
          <label>Cargo<input value={cargo} onChange={(event) => setCargo(event.target.value)} /></label>
          <Button onClick={save}>Salvar perfil</Button>
        </div>
      </Card>
    </div>
  );
}
