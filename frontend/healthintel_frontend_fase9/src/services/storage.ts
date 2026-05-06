import type { PortalUser } from '../types/domain';

const USER_KEY = 'healthintel.portal.user';
const API_KEY_KEY = 'healthintel.portal.api_key';

export function saveUser(user: PortalUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  if (user.apiKey) {
    localStorage.setItem(API_KEY_KEY, user.apiKey);
  }
}

export function getUser(): PortalUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PortalUser;
  } catch {
    return null;
  }
}

export function clearUser(): void {
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(API_KEY_KEY);
}

export function saveApiKey(apiKey: string): void {
  localStorage.setItem(API_KEY_KEY, apiKey);
  const user = getUser();
  if (user) {
    saveUser({ ...user, apiKey });
  }
}

export function getApiKey(): string {
  return localStorage.getItem(API_KEY_KEY) || '';
}
