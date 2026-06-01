"use client";

import { usePathname } from "next/navigation";
import { Bell, RefreshCw, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatRelativeTime } from "@/utils/formatters";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": { title: "Executive Dashboard", subtitle: "Real-time business overview" },
  "/sales": { title: "Sales Analytics", subtitle: "Revenue, orders, and performance metrics" },
  "/inventory": { title: "Inventory Management", subtitle: "Stock levels and warehouse utilization" },
  "/forecasting": { title: "Forecasting", subtitle: "AI-powered revenue and inventory predictions" },
  "/ai-assistant": { title: "AI Assistant", subtitle: "Conversational business intelligence" },
  "/reports": { title: "Reports", subtitle: "Generated business reports and exports" },
  "/settings": { title: "Settings", subtitle: "Platform configuration and preferences" },
};

const MOCK_NOTIFICATIONS = [
  { id: "n1", title: "Critical Stock Alert", description: "SSD-512E reaches stockout in 3 days", time: new Date(Date.now() - 5 * 60 * 1000).toISOString(), type: "critical" },
  { id: "n2", title: "Revenue Milestone", description: "Monthly revenue crossed $4.8M target", time: new Date(Date.now() - 30 * 60 * 1000).toISOString(), type: "success" },
  { id: "n3", title: "AI Insight Ready", description: "New Q4 forecast analysis available", time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), type: "info" },
  { id: "n4", title: "Branch Performance", description: "Singapore trending below target (-6.8%)", time: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), type: "warning" },
];

export function TopBar() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const queryClient = useQueryClient();

  const pageInfo = PAGE_TITLES[pathname] || { title: "ExecutiveAI", subtitle: "" };

  const handleRefresh = () => {
    queryClient.invalidateQueries();
    toast.success("Data refreshed");
  };

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-white leading-tight">{pageInfo.title}</h1>
        <p className="text-xs text-slate-400">{pageInfo.subtitle}</p>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          className="h-8 w-8"
          title="Refresh data"
        >
          <RefreshCw className="w-4 h-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="h-8 w-8"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8 relative">
              <Bell className="w-4 h-4" />
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-[10px] text-white font-bold">4</span>
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel className="flex items-center justify-between">
              <span>Notifications</span>
              <Badge variant="default" className="text-xs">4 new</Badge>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {MOCK_NOTIFICATIONS.map((n) => (
              <DropdownMenuItem key={n.id} className="flex flex-col items-start gap-1 py-3 cursor-pointer">
                <div className="flex items-center gap-2 w-full">
                  <span className={`w-2 h-2 rounded-full shrink-0 ${
                    n.type === "critical" ? "bg-red-500" :
                    n.type === "success" ? "bg-emerald-500" :
                    n.type === "warning" ? "bg-amber-500" : "bg-blue-500"
                  }`} />
                  <span className="text-sm font-medium text-white flex-1">{n.title}</span>
                  <span className="text-xs text-slate-500">{formatRelativeTime(n.time)}</span>
                </div>
                <p className="text-xs text-slate-400 pl-4">{n.description}</p>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-center justify-center text-blue-400 text-sm">
              View all notifications
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
