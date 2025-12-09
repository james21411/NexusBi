import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginUser, registerUser } from './service';

interface UserData {
  email: string | null;
  name: string | null;
}

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  user: UserData;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    user: {
      email: null,
      name: null,
    },
  });

  // Check for existing token in localStorage on initial load
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('userData');

    if (storedToken) {
      setAuthState({
        token: storedToken,
        isAuthenticated: true,
        loading: false,
        error: null,
        user: storedUser ? JSON.parse(storedUser) : { email: null, name: null },
      });
    }
  }, []);

  const login = async (email: string, password: string) => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await loginUser(email, password);

      if (response.error) {
        setAuthState(prev => ({ ...prev, error: response.error || 'Login failed', loading: false }));
        return false;
      }

      // Handle different response structures
      const token = (response.data as any)?.access_token || (response.data as any)?.token;
      if (token) {
        localStorage.setItem('authToken', token);
        localStorage.setItem('userData', JSON.stringify({ email, name: email.split('@')[0] }));

        setAuthState({
          token,
          isAuthenticated: true,
          loading: false,
          error: null,
          user: {
            email,
            name: email.split('@')[0],
          },
        });

        return true;
      }

      setAuthState(prev => ({ ...prev, error: 'Login failed: No token received', loading: false }));
      return false;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setAuthState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false,
      }));
      return false;
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    setAuthState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await registerUser(email, password, fullName);

      if (response.error) {
        setAuthState(prev => ({ ...prev, error: response.error || 'Registration failed', loading: false }));
        return false;
      }

      // After successful registration, automatically login
      return await login(email, password);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setAuthState(prev => ({
        ...prev,
        error: errorMessage,
        loading: false,
      }));
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    setAuthState({
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,
      user: {
        email: null,
        name: null,
      },
    });
  };

  const contextValue = {
    ...authState,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}

// Alias for convenience
export const useAuth = useAuthContext;