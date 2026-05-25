const ACCESS_TOKEN_KEY = 'healthintel.auth.access_token';
const REFRESH_TOKEN_KEY = 'healthintel.auth.refresh_token';
const API_KEY_KEY = 'healthintel.portal.api_key';
const API_KEY_OWNER_KEY = 'healthintel.portal.api_key_owner';

export function saveTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function saveApiKey(apiKey: string, ownerId?: string): void {
  localStorage.setItem(API_KEY_KEY, apiKey);
  if (ownerId) localStorage.setItem(API_KEY_OWNER_KEY, ownerId);
}

export function getApiKey(): string {
  return localStorage.getItem(API_KEY_KEY) || '';
}

export function getApiKeyOwner(): string | null {
  return localStorage.getItem(API_KEY_OWNER_KEY);
}

export function clearApiKey(): void {
  localStorage.removeItem(API_KEY_KEY);
  localStorage.removeItem(API_KEY_OWNER_KEY);
}

export function discardApiKeyIfOwnerMismatch(currentUserId: string): void {
  const owner = getApiKeyOwner();
  if (owner && owner !== currentUserId) {
    clearApiKey();
  }
}
