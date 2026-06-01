"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth.store";
import { authService } from "@/services/auth.service";
import type { LoginCredentials } from "@/types/auth.types";

export function useAuth() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuthStore();
  const router = useRouter();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (data) => {
      login(data.user, data.tokens);
      toast.success(`Welcome back, ${data.user.name}!`);
      router.push("/dashboard");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Login failed. Please try again.");
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      logout();
      router.push("/login");
      toast.success("Logged out successfully");
    },
    onError: () => {
      logout();
      router.push("/login");
    },
  });

  return {
    user,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    loginError: loginMutation.error,
  };
}
