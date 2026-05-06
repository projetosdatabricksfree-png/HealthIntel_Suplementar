import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { requestApi } from '../../services/apiClient';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent } from '../../services/localPortalStore';

export function AdminLayoutsPage() {
  const [result, setResult] = useState<unknown>(null);
  const { success, error } = useNotification();

  async function listarLayouts() {
    const response = await requestApi('/admin/layouts');
    setResult(response);
    addAuditEvent({
      tipo: 'admin_layouts_listar',
      usuario: 'portal_local',
      detalhe: `/admin/layouts retornou status ${response.status}.`,
      status: response.ok ? 'sucesso' : 'erro'
    });
    if (response.ok) success('Layouts retornaram da API.');
    else error(`Erro real do serviço de layouts: status ${response.status}.`);
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Layouts e compatibilidade</h1>
          <p>Integração preparada com os endpoints administrativos de layout/Mongo.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Layouts cadastrados" description="Use para governança de versões e aliases de layouts ANS." />
        <Button onClick={listarLayouts}>Listar layouts</Button>
        <CodeBlock code={JSON.stringify(result || { mensagem: 'Execute para consultar.' }, null, 2)} />
      </Card>
    </div>
  );
}
