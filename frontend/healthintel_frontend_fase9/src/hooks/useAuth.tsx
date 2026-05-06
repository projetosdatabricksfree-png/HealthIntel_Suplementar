import { createContext, useContext, useMemo, useState } from 'react';
import { demoUser } from '../data/mock';
import type { PortalUser } from '../types/domain';
import { clearUser, getUser, saveUser } from '../services/storage';
import { addAuditEvent } from '../services/localPortalStore';

interface AuthContextValue {
  user: PortalUser | null;
  isAuthenticated: boolean;
  login: (email: string, apiKey: string) => void;
  logout: () => void;
  updateUser: (user: PortalUser) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<PortalUser | null>(() => getUser());

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: Boolean(user),
    login: (email: string, apiKey: string) => {
      const nextUser = {
        ...demoUser,
        email,
        apiKey
      };
      saveUser(nextUser);
      addAuditEvent({
        tipo: 'login',
        usuario: email,
        detalhe: 'Login local no portal com API key informada.',
        status: 'sucesso'
      });
      setUser(nextUser);
    },
    logout: () => {
      addAuditEvent({
        tipo: 'logout',
        usuario: user?.email || 'usuario_local',
        detalhe: 'Sessao local encerrada.',
        status: 'sucesso'
      });
      clearUser();
      setUser(null);
    },
    updateUser: (nextUser: PortalUser) => {
      saveUser(nextUser);
      setUser(nextUser);
    }
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return value;
}
