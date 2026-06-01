export const APP_NAME = "ExecutiveAI";
export const APP_VERSION = "1.0.0";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const TIME_RANGES = [
  { label: "7 Days", value: "7d" },
  { label: "30 Days", value: "30d" },
  { label: "90 Days", value: "90d" },
  { label: "180 Days", value: "180d" },
  { label: "1 Year", value: "1y" },
  { label: "Custom", value: "custom" },
] as const;

export const FORECAST_PERIODS = [
  { label: "30 Days", value: 30 },
  { label: "90 Days", value: 90 },
  { label: "180 Days", value: 180 },
] as const;

export const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: "LayoutDashboard",
  },
  {
    label: "Sales",
    href: "/sales",
    icon: "TrendingUp",
  },
  {
    label: "Inventory",
    href: "/inventory",
    icon: "Package",
  },
  {
    label: "Forecasting",
    href: "/forecasting",
    icon: "BarChart3",
  },
  {
    label: "AI Assistant",
    href: "/ai-assistant",
    icon: "Bot",
  },
  {
    label: "Reports",
    href: "/reports",
    icon: "FileText",
  },
  {
    label: "Settings",
    href: "/settings",
    icon: "Settings",
  },
] as const;

export const CHART_COLORS = {
  primary: "#3B82F6",
  secondary: "#8B5CF6",
  success: "#10B981",
  warning: "#F59E0B",
  danger: "#EF4444",
  info: "#06B6D4",
  muted: "#64748B",
  grid: "rgba(148, 163, 184, 0.1)",
  tooltip: {
    background: "#1E293B",
    border: "#334155",
    text: "#F1F5F9",
  },
} as const;

export const SUGGESTED_QUERIES = [
  "What are my top performing products this month?",
  "Show me revenue trends for the last quarter",
  "Which branches are underperforming vs targets?",
  "What inventory items need immediate attention?",
  "What's driving the revenue growth this month?",
  "Forecast revenue for the next 90 days",
  "Which product categories have the highest margins?",
  "What are the key risks to our Q4 targets?",
] as const;

export const QUERY_KEYS = {
  dashboard: ["dashboard"],
  kpis: ["kpis"],
  sales: ["sales"],
  salesByBranch: ["sales", "branch"],
  inventory: ["inventory"],
  inventoryAlerts: ["inventory", "alerts"],
  forecasting: ["forecasting"],
  aiInsights: ["ai", "insights"],
  reports: ["reports"],
} as const;
