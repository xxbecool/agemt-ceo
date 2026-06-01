export interface User {
  id: string;
  email: string;
  name: string;
  role: "ceo" | "executive" | "analyst" | "admin";
  avatar?: string;
  company: string;
  createdAt: string;
  lastLoginAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
