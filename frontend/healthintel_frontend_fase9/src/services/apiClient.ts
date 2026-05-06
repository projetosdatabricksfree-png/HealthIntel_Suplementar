import { sampleResponse } from '../data/mock';
import { getApiKey } from './storage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
const ENABLE_DEMO_FALLBACK = String(import.meta.env.VITE_ENABLE_DEMO_FALLBACK ?? 'true') === 'true';
const ALLOWED_DEMO_MODES = new Set(['development', 'dev', 'local', 'homologacao', 'hml', 'staging', 'test']);

function canUseDemoFallback(): boolean {
  return ENABLE_DEMO_FALLBACK && ALLOWED_DEMO_MODES.has(import.meta.env.MODE);
}

export interface ApiResult {
  ok: boolean;
  status: number;
  durationMs: number;
  data: unknown;
  url: string;
}

export function buildUrl(path: string, query: Record<string, string | number | boolean | undefined> = {}): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${API_BASE_URL}${normalizedPath}`);
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && String(value).trim() !== '') {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

export async function requestApi(
  path: string,
  options: {
    method?: string;
    query?: Record<string, string | number | boolean | undefined>;
    body?: unknown;
    apiKey?: string;
  } = {}
): Promise<ApiResult> {
  const start = performance.now();
  const url = buildUrl(path, options.query);
  const headers: Record<string, string> = {
    Accept: 'application/json'
  };
  const apiKey = options.apiKey || getApiKey();

  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  if (options.body) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    });

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json')
      ? await response.json()
      : await response.text();

    return {
      ok: response.ok,
      status: response.status,
      durationMs: Math.round(performance.now() - start),
      data,
      url
    };
  } catch (error) {
    if (canUseDemoFallback()) {
      return {
        ok: true,
        status: 200,
        durationMs: Math.round(performance.now() - start),
        data: {
          ...sampleResponse,
          aviso: 'Fallback demo usado porque a API real não respondeu no navegador.',
          erro_original: error instanceof Error ? error.message : String(error)
        },
        url
      };
    }

    return {
      ok: false,
      status: 0,
      durationMs: Math.round(performance.now() - start),
      data: {
        codigo: 'FALHA_REDE',
        mensagem: error instanceof Error ? error.message : 'Falha desconhecida'
      },
      url
    };
  }
}
