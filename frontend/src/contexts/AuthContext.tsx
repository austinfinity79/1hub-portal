import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { loginApi, logoutApi, fetchMe } from '../api/auth';
import type { User } from '../types';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ACCESS_KEY = '1hub_access_token';
const REFRESH_KEY = '1hub_refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem(ACCESS_KEY),
  );
  const [loading, setLoading] = useState(!!localStorage.getItem(ACCESS_KEY));

  // On mount, if we have a stored token try to fetch current user
  useEffect(() => {
    const stored = localStorage.getItem(ACCESS_KEY);
    if (!stored) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then((u) => {
        setUser(u);
        setToken(stored);
      })
      .catch(() => {
        // Token invalid – clear
        localStorage.removeItem(ACCESS_KEY);
        localStorage.removeItem(REFRESH_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const res = await loginApi(username, password);
    localStorage.setItem(ACCESS_KEY, res.access_token);
    localStorage.setItem(REFRESH_KEY, res.refresh_token);
    setToken(res.access_token);

    const me = await fetchMe();
    setUser(me);
  }, []);

  const logout = useCallback(async () => {
    const rt = localStorage.getItem(REFRESH_KEY);
    try {
      if (rt) await logoutApi(rt);
    } catch {
      // ignore logout failures
    }
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
