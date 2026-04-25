const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const API_BASE_URL = configuredBaseUrl
  ? configuredBaseUrl.replace(/\/$/, "")
  : "";

export const DISPLAY_API_BASE_URL = API_BASE_URL || "http://localhost:8080";

export type ApiResult<T = unknown> = {
  ok: boolean;
  status: number;
  data: T | null;
  error?: string;
  elapsedMs: number;
};

export async function apiRequest<T = unknown>(
  path: string,
  apiKey?: string,
  init?: RequestInit
): Promise<ApiResult<T>> {
  const startedAt = performance.now();
  const url = path.startsWith("http") ? path : `${API_BASE_URL}${path}`;

  try {
    const headers = new Headers(init?.headers || {});
    headers.set("Accept", "application/json");

    if (apiKey?.trim()) {
      headers.set("X-API-Key", apiKey.trim());
    }

    const response = await fetch(url, {
      ...init,
      method: init?.method || "GET",
      headers
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    return {
      ok: response.ok,
      status: response.status,
      data: data as T,
      error: response.ok ? undefined : normalizeError(data),
      elapsedMs: Math.round(performance.now() - startedAt)
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      data: null,
      error: error instanceof Error ? error.message : "Erro desconhecido",
      elapsedMs: Math.round(performance.now() - startedAt)
    };
  }
}

function normalizeError(payload: unknown): string {
  if (!payload) return "Erro sem payload";
  if (typeof payload === "string") return payload;
  if (typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    return JSON.stringify(detail, null, 2);
  }
  return JSON.stringify(payload, null, 2);
}

export function maskKey(value: string): string {
  if (!value) return "Nenhuma chave configurada";
  if (value.length <= 12) return "••••••••";
  return `${value.slice(0, 7)}••••••••${value.slice(-4)}`;
}
