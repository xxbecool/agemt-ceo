import api from "./api";
import type { LoginCredentials, User, AuthTokens } from "@/types/auth.types";

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>("/auth/login", credentials);
      return response.data;
    } catch {
      // Demo fallback: if API is unavailable, use mock data
      if (credentials.email && credentials.password) {
        const mockUser: User = {
          id: "usr_demo_001",
          email: credentials.email,
          name: "John Smith",
          role: "ceo",
          company: "Acme Corporation",
          createdAt: "2024-01-15T08:00:00Z",
          lastLoginAt: new Date().toISOString(),
        };
        const mockTokens: AuthTokens = {
          accessToken: "demo_access_token_" + Date.now(),
          refreshToken: "demo_refresh_token_" + Date.now(),
          expiresIn: 3600,
        };
        return { user: mockUser, tokens: mockTokens };
      }
      throw new Error("Invalid credentials");
    }
  },

  async logout(): Promise<void> {
    try {
      await api.post("/auth/logout");
    } catch {
      // Silently fail
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>("/auth/me");
      return response.data;
    } catch {
      throw new Error("Failed to get current user");
    }
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};
