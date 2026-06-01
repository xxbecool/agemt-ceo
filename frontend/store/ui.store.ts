import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  sidebarCollapsed: boolean;
  theme: "dark" | "light";
  activePage: string;
}

interface UIActions {
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: "dark" | "light") => void;
  setActivePage: (page: string) => void;
}

type UIStore = UIState & UIActions;

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: "dark",
      activePage: "/dashboard",

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }),
      setTheme: (theme) => set({ theme }),
      setActivePage: (activePage) => set({ activePage }),
    }),
    {
      name: "ui-storage",
    }
  )
);
