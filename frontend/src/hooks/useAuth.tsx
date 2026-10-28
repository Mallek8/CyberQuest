import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { api, TOKEN_KEY, UNAUTHORIZED_EVENT } from "../services/apiClient";
import type { AuthResponse, User } from "../types/api";
import type { LoginValues, RegisterValues } from "../features/auth/schemas";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (values: LoginValues) => Promise<void>;
  registerAccount: (values: RegisterValues) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);

  const meQuery = useQuery({
    queryKey: ["me", token],
    queryFn: () => api<User>("/auth/me"),
    enabled: Boolean(token),
    retry: false,
  });

  useEffect(() => {
    if (meQuery.data) {
      setUser(meQuery.data);
    }
  }, [meQuery.data]);

  useEffect(() => {
    const onUnauthorized = () => {
      setToken(null);
      setUser(null);
      queryClient.clear();
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, [queryClient]);

  async function login(values: LoginValues) {
    const result = await api<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(values),
    });
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    setUser(result.user);
  }

  async function registerAccount(values: RegisterValues) {
    const result = await api<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: values.email,
        username: values.username,
        display_name: values.displayName,
        password: values.password,
      }),
    });
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    setUser(result.user);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    queryClient.clear();
  }

  const loading = Boolean(token) && !user && meQuery.isLoading;

  return (
    <AuthContext.Provider value={{ user, loading, login, registerAccount, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return value;
}
