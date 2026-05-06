import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { requestApi } from '../../services/apiClient';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent } from '../../services/localPortalStore';

export function AdminBillingPage() {
  const [referencia, setReferencia] = useState('2026-05');
  const [result, setResult] = useState<unknown>(null);
  const { success, error } = useNotification();

  async function buscarResumo() {
    const response = await requestApi('/admin/billing/resumo', { query: { referencia } });
    setResult(response);
    addAuditEvent({
      tipo: 'admin_billing_resumo',
      usuario: 'portal_local',
      detalhe: `/admin/billing/resumo retornou status ${response.status}.`,
      status: response.ok ? 'sucesso' : 'erro'
    });
    if (response.ok) success('Resumo admin retornou da API.');
    else error(`Erro real da API admin: status ${response.status}.`);
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Billing administrativo</h1>
          <p>Integração preparada com endpoints `/admin/billing` existentes no backend.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Resumo de faturamento" description="Requer chave com plano/permissão administrativa." />
        <div className="form-grid single">
          <label>Referência<input value={referencia} onChange={(event) => setReferencia(event.target.value)} /></label>
          <Button onClick={buscarResumo}>Buscar resumo</Button>
        </div>
        <CodeBlock code={JSON.stringify(result || { mensagem: 'Execute para consultar.' }, null, 2)} />
      </Card>
    </div>
  );
}
