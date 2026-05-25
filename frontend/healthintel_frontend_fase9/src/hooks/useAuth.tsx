import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { AuthUser } from '../types/domain';
import { authApi } from '../services/authApi';
import { clearTokens, discardApiKeyIfOwnerMismatch, getAccessToken, getRefreshToken, saveTokens } from '../services/storage';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, senha: string) => Promise<void>;
  loginWithGoogle: (id_token: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function _perfilToAuthUser(perfil: Awaited<ReturnType<typeof authApi.perfil>>): AuthUser {
  const tenants = perfil.tenants ?? [];
  const tenant_ativo = tenants[0] ?? null;
  return {
    id: perfil.id,
    email: perfil.email,
    nome: perfil.nome,
    avatar_url: perfil.avatar_url,
    status: perfil.status,
    email_verificado: perfil.email_verificado,
    tenants,
    tenant_ativo,
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scheduleRefresh = useCallback(() => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    // Refresh 2 minutos antes de expirar (access TTL = 15 min → refresh em 13 min)
    refreshTimerRef.current = setTimeout(async () => {
      const rt = getRefreshToken();
      if (!rt) return;
      try {
        const res = await authApi.refresh(rt);
        saveTokens(res.access_token, res.refresh_token);
        scheduleRefresh();
      } catch {
        clearTokens();
        setUser(null);
      }
    }, 13 * 60 * 1000);
  }, []);

  // Bootstrap: tenta carregar sessão existente
  useEffect(() => {
    async function bootstrap() {
      const at = getAccessToken();
      const rt = getRefreshToken();
      if (!at || !rt) {
        setIsLoading(false);
        return;
      }
      try {
        const perfil = await authApi.perfil(at);
        setUser(_perfilToAuthUser(perfil));
        scheduleRefresh();
      } catch {
        // Tenta refresh se access expirou
        try {
          const refreshed = await authApi.refresh(rt);
          saveTokens(refreshed.access_token, refreshed.refresh_token);
          const perfil = await authApi.perfil(refreshed.access_token);
          setUser(_perfilToAuthUser(perfil));
          scheduleRefresh();
        } catch {
          clearTokens();
        }
      } finally {
        setIsLoading(false);
      }
    }
    bootstrap();
    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [scheduleRefresh]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: Boolean(user),
    isLoading,

    login: async (email: string, senha: string) => {
      const res = await authApi.login(email, senha);
      saveTokens(res.access_token, res.refresh_token);
      const perfil = await authApi.perfil(res.access_token);
      discardApiKeyIfOwnerMismatch(perfil.id);
      setUser(_perfilToAuthUser(perfil));
      scheduleRefresh();
    },

    loginWithGoogle: async (id_token: string) => {
      const res = await authApi.loginGoogle(id_token);
      saveTokens(res.access_token, res.refresh_token);
      const perfil = await authApi.perfil(res.access_token);
      discardApiKeyIfOwnerMismatch(perfil.id);
      setUser(_perfilToAuthUser(perfil));
      scheduleRefresh();
    },

    logout: async () => {
      const rt = getRefreshToken();
      const at = getAccessToken();
      if (rt) {
        try { await authApi.logout(rt); } catch { /* best-effort */ }
      }
      if (at) {
        try { await authApi.logoutTudo(at); } catch { /* best-effort */ }
      }
      clearTokens();
      setUser(null);
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    },

    refreshUser: async () => {
      const at = getAccessToken();
      if (!at) return;
      const perfil = await authApi.perfil(at);
      setUser(_perfilToAuthUser(perfil));
    },
  }), [user, isLoading, scheduleRefresh]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return value;
}
