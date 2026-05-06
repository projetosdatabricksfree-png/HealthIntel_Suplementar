import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { useNotification } from '../../components/NotificationProvider';
import { buildCurl, maskApiKey, requestApi, type ApiResult } from '../../services/apiClient';
import { clearApiKey, getApiKey, saveApiKey } from '../../services/storage';
import { useAuth } from '../../hooks/useAuth';
import { addAuditEvent } from '../../services/localPortalStore';

export function ApiKeysPage() {
  const { user, updateUser } = useAuth();
  const { success, error, info } = useNotification();
  const [apiKey, setApiKey] = useState(getApiKey());
  const [testResult, setTestResult] = useState<ApiResult | null>(null);

  function save() {
    const normalized = apiKey.trim();
    if (!normalized) {
      error('Informe uma API key antes de salvar.');
      return;
    }
    saveApiKey(normalized);
    if (user) updateUser({ ...user, apiKey: normalized });
    addAuditEvent({
      tipo: 'salvar_api_key',
      usuario: user?.email || 'portal_local',
      detalhe: `Chave salva localmente: ${maskApiKey(normalized)}.`,
      status: 'sucesso'
    });
    success('API key salva localmente.');
  }

  function clear() {
    clearApiKey();
    setApiKey('');
    if (user) updateUser({ ...user, apiKey: '' });
    addAuditEvent({
      tipo: 'limpar_api_key',
      usuario: user?.email || 'portal_local',
      detalhe: 'API key removida do localStorage.',
      status: 'sucesso'
    });
    info('API key local removida.');
  }

  async function test() {
    const response = await requestApi('/v1/meta/endpoints', { apiKey: apiKey.trim() });
    setTestResult(response);
    addAuditEvent({
      tipo: 'testar_api_key',
      usuario: user?.email || 'portal_local',
      detalhe: `/v1/meta/endpoints retornou status ${response.status}.`,
      status: response.ok ? 'sucesso' : 'erro'
    });
    if (response.ok) success('Chave válida para chamada de teste.');
    else error(response.status === 401 ? 'Chave inválida.' : response.status === 403 ? 'Chave sem permissão.' : 'API indisponível ou retornou erro.');
  }

  async function copyMasked() {
    await navigator.clipboard.writeText(maskApiKey(apiKey.trim()));
    success('Chave mascarada copiada.');
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
            <Button variant="secondary" onClick={clear}>Limpar chave</Button>
            <Button variant="secondary" onClick={test}>Testar chave</Button>
            <Button variant="ghost" onClick={copyMasked}>Copiar chave mascarada</Button>
          </div>
          <CodeBlock code={buildCurl('GET', 'http://localhost:8080/v1/meta/endpoints', apiKey.trim())} />
          {testResult && <CodeBlock code={JSON.stringify(testResult, null, 2)} />}
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
