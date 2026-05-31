'use client';

import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext({
  user: null,
  session: null,
  loading: true,
  signInWithGoogle: async () => ({ error: new Error('Auth disabled in local-only mode') }),
  signInWithEmail: async () => ({ error: new Error('Auth disabled in local-only mode') }),
  signOut: async () => {},
});

export function AuthProvider({ children }) {
  // Local-only mode: no Supabase, no sessions.
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: null,
        session: null,
        loading,
        signInWithGoogle: async () => ({ error: new Error('Auth disabled in local-only mode') }),
        signInWithEmail: async () => ({ error: new Error('Auth disabled in local-only mode') }),
        signOut: async () => {},
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
