import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { useAuth } from '../../hooks/useAuth';

export function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [nome, setNome] = useState(user?.nome || '');
  const [empresa, setEmpresa] = useState(user?.empresa || '');
  const [cargo, setCargo] = useState(user?.cargo || '');

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
          <Button onClick={() => user && updateUser({ ...user, nome, empresa, cargo })}>Salvar perfil</Button>
        </div>
      </Card>
    </div>
  );
}
