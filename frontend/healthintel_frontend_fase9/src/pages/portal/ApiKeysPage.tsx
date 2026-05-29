import { useCallback, useEffect, useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { useNotification } from '../../components/NotificationProvider';
import { buildCurl, buildUrl, maskApiKey, requestApi } from '../../services/apiClient';
import { clearApiKey, getAccessToken, getApiKey, saveApiKey } from '../../services/storage';
import { useAuth } from '../../hooks/useAuth';
import { getCurrentPlan } from '../../data/planRules';
import type { PortalApiKey } from '../../types/domain';

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

export function ApiKeysPage() {
  const { user } = useAuth();
  const { success, error } = useNotification();
  const [keys, setKeys] = useState<PortalApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeApiKey, setActiveApiKey] = useState(getApiKey());
  const [testStatus, setTestStatus] = useState<{ ok: boolean; mensagem: string } | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newKeyName, setNewKeyName] = useState('Produção principal');
  const [newKeyAmbiente, setNewKeyAmbiente] = useState<'sandbox' | 'producao'>('sandbox');
  const [oneTimeSecret, setOneTimeSecret] = useState('');
  const [creating, setCreating] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; nome: string } | null>(null);
  const [deleting, setDeleting] = useState(false);
  const currentPlan = getCurrentPlan(user?.tenant_ativo?.plano_nome);

  const loadKeys = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch<{ dados: PortalApiKey[] }>('/v1/portal/api-keys');
      setKeys(data.dados);
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao carregar chaves.');
    } finally {
      setLoading(false);
    }
  }, [error]);

  useEffect(() => { void loadKeys(); }, [loadKeys]);

  async function createKey() {
    if (!newKeyName.trim()) { error('Informe um nome para a chave.'); return; }
    setCreating(true);
    try {
      const data = await apiFetch<{ dados: { id: string; chave_plain: string; prefixo: string; nome: string; ambiente: string; criado_em: string } }>(
        '/v1/portal/api-keys', 'POST', { nome: newKeyName.trim(), ambiente: newKeyAmbiente }
      );
      setOneTimeSecret(data.dados.chave_plain);
      saveApiKey(data.dados.chave_plain, user?.id);
      setActiveApiKey(data.dados.chave_plain);
      setShowCreate(false);
      setNewKeyName('Produção principal');
      await loadKeys();
      success('Chave criada. Copie agora — ela não será exibida novamente.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao criar chave.');
    } finally {
      setCreating(false);
    }
  }

  function askDelete(id: string, nome: string | null) {
    setDeleteTarget({ id, nome: nome || 'sem nome' });
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await apiFetch(`/v1/portal/api-keys/${deleteTarget.id}/revogar`, 'POST');
      await loadKeys();
      success('Chave excluída.');
      setDeleteTarget(null);
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao excluir.');
    } finally {
      setDeleting(false);
    }
  }

  async function rotateKey(id: string) {
    try {
      const data = await apiFetch<{ dados: { chave_plain: string } }>(`/v1/portal/api-keys/${id}/rotacionar`, 'POST');
      setOneTimeSecret(data.dados.chave_plain);
      saveApiKey(data.dados.chave_plain, user?.id);
      setActiveApiKey(data.dados.chave_plain);
      await loadKeys();
      success('Chave rotacionada. Copie a nova chave agora.');
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao rotacionar.');
    }
  }

  async function toggleKey(id: string, currentStatus: string) {
    const action = currentStatus === 'ativo' ? 'desabilitar' : 'habilitar';
    try {
      await apiFetch(`/v1/portal/api-keys/${id}/${action}`, 'POST');
      await loadKeys();
      success(action === 'desabilitar' ? 'Chave desabilitada.' : 'Chave habilitada.');
    } catch (err) {
      error(err instanceof Error ? err.message : `Erro ao ${action}.`);
    }
  }

  async function test() {
    const response = await requestApi('/v1/meta/endpoints', { apiKey: activeApiKey.trim() });
    if (response.ok) {
      setTestStatus({ ok: true, mensagem: 'Chave válida.' });
      success('Chave válida.');
      return;
    }
    const mensagem = response.status === 401
      ? 'Chave inválida.'
      : response.status === 403
        ? 'Chave sem permissão neste plano.'
        : 'Não foi possível validar a chave agora.';
    setTestStatus({ ok: false, mensagem });
    error(mensagem);
  }

  async function copyOneTimeSecret() {
    await navigator.clipboard.writeText(oneTimeSecret);
    success('Chave completa copiada.');
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">API keys</p>
          <h1>Gerencie suas chaves de API</h1>
          <p>Use as chaves somente no header <code>X-API-Key</code>. Elas não fazem login no portal.</p>
        </div>
      </div>

      {oneTimeSecret && (
        <Card>
          <CardHeader title="Copie sua chave agora" description="A chave completa aparece somente uma vez." />
          <CodeBlock code={oneTimeSecret} />
          <div className="button-row">
            <Button onClick={() => void copyOneTimeSecret()}>Copiar chave completa</Button>
            <Button variant="secondary" onClick={() => setOneTimeSecret('')}>Já copiei</Button>
          </div>
        </Card>
      )}

      <Card>
        <CardHeader title="Chaves do cliente" description={`Plano ${currentPlan.nome}: limite de ${currentPlan.keyLimit} chave(s) ativa(s).`} />
        {loading ? (
          <div className="empty-state-inline">Carregando chaves…</div>
        ) : keys.length === 0 ? (
          <div className="empty-state-inline">Nenhuma chave criada. Crie sua primeira API key para testar endpoints reais.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Nome</th><th>Prefixo</th><th>Ambiente</th><th>Criada em</th><th>Último uso</th><th>Status</th><th>Ações</th></tr>
              </thead>
              <tbody>
                {keys.map((key) => (
                  <tr key={key.id}>
                    <td>{key.nome || '—'}</td>
                    <td><code>{key.prefixo}</code></td>
                    <td>{key.ambiente}</td>
                    <td>{new Date(key.criado_em).toLocaleDateString('pt-BR')}</td>
                    <td>{key.ultimo_uso_em ? new Date(key.ultimo_uso_em).toLocaleString('pt-BR') : 'Nunca'}</td>
                    <td>
                      <span className={`status-pill status-pill--${key.status === 'ativo' ? 'disponivel' : 'sem_dados'}`}>{key.status}</span>
                    </td>
                    <td>
                      <div className="button-row">
                        {key.status === 'ativo' && (
                          <>
                            <Button variant="ghost" onClick={() => void rotateKey(key.id)}>Rotacionar</Button>
                            <Button variant="secondary" onClick={() => void toggleKey(key.id, key.status)}>Desabilitar</Button>
                          </>
                        )}
                        {key.status === 'desabilitado' && (
                          <Button variant="secondary" onClick={() => void toggleKey(key.id, key.status)}>Habilitar</Button>
                        )}
                        {(key.status === 'ativo' || key.status === 'desabilitado') && (
                          <Button variant="danger" onClick={() => askDelete(key.id, key.nome)}>Excluir</Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="button-row">
          <Button onClick={() => setShowCreate(true)}>Criar nova chave</Button>
          <Button variant="secondary" onClick={() => void loadKeys()}>Atualizar</Button>
        </div>
      </Card>

      {deleteTarget && (
        <Card className="modal-card">
          <CardHeader title="Excluir chave de API" description="A chave deixará de funcionar imediatamente e essa ação não pode ser desfeita." />
          <p>
            Tem certeza que deseja excluir a chave <strong>{deleteTarget.nome}</strong>?
          </p>
          <div className="button-row">
            <Button variant="danger" onClick={() => void confirmDelete()} disabled={deleting}>{deleting ? 'Excluindo…' : 'Excluir'}</Button>
            <Button variant="secondary" onClick={() => setDeleteTarget(null)} disabled={deleting}>Cancelar</Button>
          </div>
        </Card>
      )}

      {showCreate && (
        <Card className="modal-card">
          <CardHeader title="Criar nova chave" description="A chave completa será exibida apenas uma vez após a criação." />
          <div className="form-grid single">
            <label>Nome<input value={newKeyName} onChange={(event) => setNewKeyName(event.target.value)} /></label>
            <label>
              Ambiente
              <select value={newKeyAmbiente} onChange={(event) => setNewKeyAmbiente(event.target.value as 'sandbox' | 'producao')}>
                <option value="sandbox">sandbox</option>
                <option value="producao" disabled={currentPlan.slug === 'free'}>producao{currentPlan.slug === 'free' ? ' (requer plano pago)' : ''}</option>
              </select>
            </label>
            <div className="button-row">
              <Button onClick={() => void createKey()} disabled={creating}>{creating ? 'Criando…' : 'Criar chave'}</Button>
              <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancelar</Button>
            </div>
          </div>
        </Card>
      )}

      <div className="split-grid">
        <Card>
          <CardHeader title="Teste rápido" description="Executa uma chamada real contra /v1/meta/endpoints." />
          <label className="field-label">
            Chave ativa no navegador
            <input value={activeApiKey} onChange={(event) => setActiveApiKey(event.target.value)} />
          </label>
          <div className="button-row">
            <Button onClick={() => { saveApiKey(activeApiKey.trim(), user?.id); success('Chave ativa salva.'); }}>Salvar chave ativa</Button>
            <Button variant="secondary" onClick={() => void test()} disabled={!activeApiKey.trim()}>Testar chave</Button>
            <Button variant="ghost" onClick={() => { clearApiKey(); setActiveApiKey(''); }}>Limpar</Button>
          </div>
          <CodeBlock code={buildCurl('GET', buildUrl('/v1/meta/endpoints'), activeApiKey.trim())} />
          {testStatus && (
            <p className={testStatus.ok ? 'status-item--ok' : 'status-item--error'} style={{ margin: '0.75rem 0 0', fontWeight: 700 }}>
              {testStatus.mensagem}
            </p>
          )}
        </Card>

        <Card>
          <CardHeader title="Boas práticas" description="Aplique estas regras fora do navegador." />
          <ul className="check-list">
            <li>Nunca use API key para login no portal.</li>
            <li>Use <code>hi_test_</code> em sandbox e <code>hi_live_</code> em produção.</li>
            <li>Exclua chaves vazadas imediatamente.</li>
            <li>Rotacione periodicamente chaves de produção.</li>
            <li>Chave ativa atual: {maskApiKey(activeApiKey)}</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
