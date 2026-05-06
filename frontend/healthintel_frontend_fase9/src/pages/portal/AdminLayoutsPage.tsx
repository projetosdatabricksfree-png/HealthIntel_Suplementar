import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { requestApi } from '../../services/apiClient';

export function AdminLayoutsPage() {
  const [result, setResult] = useState<unknown>(null);

  async function listarLayouts() {
    setResult(await requestApi('/admin/layouts'));
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
