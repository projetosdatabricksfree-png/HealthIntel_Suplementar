import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';
import { buildUrl } from '../../services/apiClient';
import { getAccessToken } from '../../services/storage';

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const { success, error } = useNotification();
  const [nome, setNome] = useState(user?.nome || '');
  const [saving, setSaving] = useState(false);

  async function save() {
    if (!nome.trim()) {
      error('Informe seu nome.');
      return;
    }
    setSaving(true);
    try {
      const at = getAccessToken();
      if (!at) throw new Error('Sessão expirada.');
      const res = await fetch(buildUrl('/v1/me/perfil'), {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${at}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: nome.trim() }),
      });
      if (!res.ok) throw new Error('Falha ao salvar.');
      await refreshUser();
      success('Perfil atualizado.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Falha ao salvar perfil.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Perfil</p>
          <h1>Dados da conta</h1>
          <p>Informações da sua conta HealthIntel.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Informações principais" description="Dados vinculados à sua conta." />
        <div className="form-grid">
          <label>Nome<input value={nome} onChange={(e) => setNome(e.target.value)} /></label>
          <label>E-mail<input value={user?.email || ''} disabled /></label>
          <label>Organização<input value={user?.tenant_ativo?.nome || '—'} disabled /></label>
          <label>Plano<input value={user?.tenant_ativo?.plano_nome || '—'} disabled /></label>
          <Button onClick={() => void save()} disabled={saving}>
            {saving ? 'Salvando…' : 'Salvar nome'}
          </Button>
        </div>
      </Card>
    </div>
  );
}
