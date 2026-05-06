import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { liveTesterEndpoints } from '../../data/endpoints';
import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { requestApi, type ApiResult } from '../../services/apiClient';
import type { ApiEndpoint } from '../../types/domain';
import { getApiKey } from '../../services/storage';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent } from '../../services/localPortalStore';

function resolvePath(path: string, registroAns: string, municipio: string, uf: string) {
  return path
    .replace('{registro_ans}', registroAns || '000000')
    .replace('{cd_municipio}', municipio || '3550308')
    .replace('{sg_uf}', uf || 'SP');
}

export function ExplorerPage() {
  const [searchParams] = useSearchParams();
  const { success, error } = useNotification();
  const initialEndpoint = searchParams.get('endpoint') || 'operadoras';
  const [endpointId, setEndpointId] = useState(
    liveTesterEndpoints.some((item) => item.id === initialEndpoint) ? initialEndpoint : 'operadoras'
  );
  const [registroAns, setRegistroAns] = useState('123456');
  const [municipio, setMunicipio] = useState('3550308');
  const [uf, setUf] = useState('SP');
  const [pagina, setPagina] = useState('1');
  const [porPagina, setPorPagina] = useState('20');
  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);

  const endpoint = useMemo<ApiEndpoint>(
    () => liveTesterEndpoints.find((item) => item.id === endpointId) || liveTesterEndpoints[0],
    [endpointId]
  );
  const resolvedPath = resolvePath(endpoint.path, registroAns, municipio, uf);
  const normalizedPagina = Math.max(Number.parseInt(pagina, 10) || 1, 1);
  const normalizedPorPagina = Math.min(Math.max(Number.parseInt(porPagina, 10) || 20, 1), 100);

  async function run() {
    setLoading(true);
    const response = await requestApi(resolvedPath, {
      method: endpoint.method,
      apiKey: getApiKey(),
      query: {
        uf: endpoint.path.includes('operadoras') && !endpoint.path.includes('{registro_ans}') ? uf : undefined,
        pagina: endpoint.method === 'GET' && endpoint.authRequired ? normalizedPagina : undefined,
        por_pagina: endpoint.method === 'GET' && endpoint.authRequired ? normalizedPorPagina : undefined
      }
    });
    setResult(response);
    addAuditEvent({
      tipo: 'chamada_api_explorer',
      usuario: 'portal_local',
      detalhe: `${endpoint.method} ${resolvedPath} retornou status ${response.status}.`,
      status: response.ok ? 'sucesso' : 'erro'
    });
    if (response.ok) success(`Endpoint executado com status ${response.status}.`);
    else error(`Falha ao executar endpoint. Status ${response.status}.`);
    setLoading(false);
  }

  async function copyCurl() {
    const curl = result?.curl || `GET ${resolvedPath}`;
    await navigator.clipboard.writeText(curl);
    success('cURL copiado.');
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Live tester</p>
          <h1>Teste a API direto do portal</h1>
          <p>Escolha um endpoint, preencha variáveis e execute com sua API key.</p>
        </div>
      </div>

      <div className="split-grid split-grid-wide">
        <Card>
          <CardHeader title="Requisição" description="O tester usa `X-API-Key` salvo no portal." />
          <div className="form-grid single">
            <label>
              Endpoint
              <select value={endpointId} onChange={(event) => setEndpointId(event.target.value)}>
                {liveTesterEndpoints.map((item) => (
                  <option key={item.id} value={item.id}>{item.method} {item.path}</option>
                ))}
              </select>
            </label>
            <label>
              Registro ANS
              <input value={registroAns} onChange={(event) => setRegistroAns(event.target.value)} />
            </label>
            <label>
              Código município
              <input value={municipio} onChange={(event) => setMunicipio(event.target.value)} />
            </label>
            <label>
              UF
              <input value={uf} onChange={(event) => setUf(event.target.value.toUpperCase())} />
            </label>
            <label>
              Página
              <input
                type="number"
                min="1"
                value={pagina}
                onChange={(event) => setPagina(event.target.value)}
              />
            </label>
            <label>
              Registros por página
              <input
                type="number"
                min="1"
                max="100"
                value={porPagina}
                onChange={(event) => setPorPagina(event.target.value)}
              />
            </label>
            <Button type="button" onClick={run} disabled={loading}>
              {loading ? 'Executando...' : 'Executar'}
            </Button>
          </div>
          <div className="button-row">
            <Button type="button" variant="secondary" onClick={copyCurl}>Copiar cURL</Button>
            <Button type="button" variant="ghost" onClick={() => setResult(null)}>Limpar resposta</Button>
          </div>
          <CodeBlock code={(result?.curl) || `${endpoint.method} ${resolvedPath}\nX-API-Key: ${getApiKey() ? 'configurada' : 'não configurada'}`} />
        </Card>

        <Card>
          <CardHeader title="Resposta" description="JSON retornado pela API real ou erro real de rede/permissão." />
          {result && (
            <div className="response-meta">
              <span>Status HTTP: <strong>{result.status}</strong></span>
              <span>Tempo: <strong>{result.durationMs} ms</strong></span>
              <span>Método: <strong>{result.method}</strong></span>
            </div>
          )}
          <CodeBlock code={JSON.stringify(result || { mensagem: 'Execute uma chamada para ver o resultado.' }, null, 2)} />
        </Card>
      </div>
    </div>
  );
}
