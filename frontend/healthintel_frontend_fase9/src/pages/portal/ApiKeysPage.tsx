import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { getApiKey, saveApiKey } from '../../services/storage';
import { useAuth } from '../../hooks/useAuth';

export function ApiKeysPage() {
  const { user, updateUser } = useAuth();
  const [apiKey, setApiKey] = useState(getApiKey());

  function save() {
    saveApiKey(apiKey);
    if (user) updateUser({ ...user, apiKey });
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">API keys</p>
          <h1>Gerencie sua chave de API</h1>
          <p>Na API atual, o acesso é feito via header `X-API-Key`.</p>
        </div>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Chave ativa" description="Use uma chave real do banco `plataforma.chave_api` em homologação/produção." />
          <label className="field-label">
            API key
            <input value={apiKey} onChange={(event) => setApiKey(event.target.value)} />
          </label>
          <div className="button-row">
            <Button onClick={save}>Salvar chave local</Button>
            <Button variant="secondary" onClick={() => setApiKey('')}>Limpar</Button>
          </div>
        </Card>

        <Card>
          <CardHeader title="Controles recomendados" description="Preparado para a gestão comercial do DaaS." />
          <ul className="check-list">
            <li>Uma chave por cliente/projeto.</li>
            <li>Whitelist de domínio ou IP por plano.</li>
            <li>Rotação de chave.</li>
            <li>Revogação imediata em caso de abuso.</li>
            <li>Limite por minuto e por mês.</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
