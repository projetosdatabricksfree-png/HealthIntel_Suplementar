import { createContext, useContext, useMemo, useState } from 'react';
import { demoUser } from '../data/mock';
import type { PortalUser } from '../types/domain';
import { clearUser, getUser, saveUser } from '../services/storage';

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
      setUser(nextUser);
    },
    logout: () => {
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
