"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  TrendingUp,
  Package,
  BarChart3,
  Bot,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
  LogOut,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useUIStore } from "@/store/ui.store";
import { useAuthStore } from "@/store/auth.store";
import { useAuth } from "@/hooks/useAuth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Sales", href: "/sales", icon: TrendingUp },
  { label: "Inventory", href: "/inventory", icon: Package },
  { label: "Forecasting", href: "/forecasting", icon: BarChart3 },
  { label: "AI Assistant", href: "/ai-assistant", icon: Bot },
  { label: "Reports", href: "/reports", icon: FileText },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { user } = useAuthStore();
  const { logout } = useAuth();

  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "EU";

  return (
    <TooltipProvider delayDuration={0}>
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 64 : 240 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
        className="relative flex flex-col h-screen bg-slate-900 border-r border-slate-700/50 overflow-hidden shrink-0 z-20"
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-3 border-b border-slate-700/50">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <AnimatePresence mode="wait">
              {!sidebarCollapsed && (
                <motion.span
                  key="logo-text"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.2 }}
                  className="font-bold text-white text-base whitespace-nowrap"
                >
                  ExecutiveAI
                </motion.span>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            const linkContent = (
              <Link
                href={item.href}
                className={cn(
                  "sidebar-item",
                  isActive && "active",
                  sidebarCollapsed && "justify-center px-0"
                )}
              >
                <Icon className="w-5 h-5 shrink-0" />
                <AnimatePresence mode="wait">
                  {!sidebarCollapsed && (
                    <motion.span
                      key={`label-${item.href}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="truncate"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            );

            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                  <TooltipContent side="right">{item.label}</TooltipContent>
                </Tooltip>
              );
            }

            return <div key={item.href}>{linkContent}</div>;
          })}
        </nav>

        {/* User section */}
        <div className="border-t border-slate-700/50 p-2">
          <div
            className={cn(
              "flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-slate-700/50 transition-colors cursor-pointer group",
              sidebarCollapsed && "justify-center px-0"
            )}
          >
            <Avatar className="w-8 h-8 shrink-0">
              <AvatarFallback className="text-xs bg-blue-600/30 text-blue-300">
                {initials}
              </AvatarFallback>
            </Avatar>
            <AnimatePresence mode="wait">
              {!sidebarCollapsed && (
                <motion.div
                  key="user-info"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="flex-1 min-w-0"
                >
                  <p className="text-sm font-medium text-white truncate">
                    {user?.name || "Executive User"}
                  </p>
                  <p className="text-xs text-slate-400 truncate capitalize">
                    {user?.role || "CEO"}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
            <AnimatePresence mode="wait">
              {!sidebarCollapsed && (
                <motion.button
                  key="logout-btn"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => logout()}
                  className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-white transition-all p-1 rounded"
                >
                  <LogOut className="w-4 h-4" />
                </motion.button>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Collapse button */}
        <button
          onClick={toggleSidebar}
          className="absolute top-1/2 -right-3 transform -translate-y-1/2 w-6 h-6 bg-slate-700 border border-slate-600 rounded-full flex items-center justify-center hover:bg-slate-600 transition-colors z-30"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-3 h-3 text-slate-300" />
          ) : (
            <ChevronLeft className="w-3 h-3 text-slate-300" />
          )}
        </button>
      </motion.aside>
    </TooltipProvider>
  );
}
