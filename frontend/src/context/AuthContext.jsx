import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as loginRequest } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authUser, setAuthUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  async function loadMe() {
    try {
      const data = await getMe();
      setAuthUser(data.user);
      setTenant(data.tenant);
    } catch (error) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setAuthUser(null);
      setTenant(null);
    } finally {
      setLoadingAuth(false);
    }
  }

  async function signIn(username, password) {
    setLoadingAuth(true);

    const data = await loginRequest({ username, password });

    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);

    console.log("TOKEN SALVO:", localStorage.getItem("access_token"));

    await loadMe();
  }

  function signOut() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setAuthUser(null);
    setTenant(null);
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (token) {
      loadMe();
    } else {
      setLoadingAuth(false);
    }
  }, []);

  const value = useMemo(
    () => ({
      authUser,
      tenant,
      loadingAuth,
      signIn,
      signOut,
      reloadMe: loadMe,
    }),
    [authUser, tenant, loadingAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}