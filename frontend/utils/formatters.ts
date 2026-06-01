import { format, formatDistanceToNow, parseISO } from "date-fns";

export function formatCurrency(
  value: number,
  options?: { compact?: boolean; decimals?: number }
): string {
  const { compact = false, decimals = 2 } = options || {};

  if (compact) {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    if (value >= 1_000) {
      return `$${(value / 1_000).toFixed(1)}K`;
    }
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatNumber(
  value: number,
  options?: { compact?: boolean; decimals?: number }
): string {
  const { compact = false, decimals = 0 } = options || {};

  if (compact) {
    if (value >= 1_000_000_000) {
      return `${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (value >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(1)}M`;
    }
    if (value >= 1_000) {
      return `${(value / 1_000).toFixed(1)}K`;
    }
  }

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatPercentage(
  value: number,
  options?: { decimals?: number; showSign?: boolean }
): string {
  const { decimals = 1, showSign = false } = options || {};
  const formatted = `${Math.abs(value).toFixed(decimals)}%`;
  if (showSign && value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

export function formatDate(
  date: string | Date,
  formatStr: string = "MMM dd, yyyy"
): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  return format(d, formatStr);
}

export function formatDateShort(date: string | Date): string {
  return formatDate(date, "MMM dd");
}

export function formatDateTime(date: string | Date): string {
  return formatDate(date, "MMM dd, yyyy HH:mm");
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  return formatDistanceToNow(d, { addSuffix: true });
}

export function formatKPIValue(
  value: number,
  format: "currency" | "percentage" | "number" | "count"
): string {
  switch (format) {
    case "currency":
      return formatCurrency(value, { compact: true });
    case "percentage":
      return formatPercentage(value);
    case "number":
      return formatNumber(value, { compact: true });
    case "count":
      return formatNumber(value, { compact: true });
    default:
      return String(value);
  }
}

export function getTrendColor(change: number): string {
  if (change > 0) return "text-emerald-400";
  if (change < 0) return "text-red-400";
  return "text-slate-400";
}

export function getSeverityColor(
  severity: "critical" | "warning" | "info"
): string {
  switch (severity) {
    case "critical":
      return "text-red-400 bg-red-400/10 border-red-400/20";
    case "warning":
      return "text-amber-400 bg-amber-400/10 border-amber-400/20";
    case "info":
      return "text-blue-400 bg-blue-400/10 border-blue-400/20";
  }
}

export function getStatusColor(
  status: "in_stock" | "low_stock" | "critical" | "out_of_stock"
): string {
  switch (status) {
    case "in_stock":
      return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20";
    case "low_stock":
      return "text-amber-400 bg-amber-400/10 border-amber-400/20";
    case "critical":
      return "text-red-400 bg-red-400/10 border-red-400/20";
    case "out_of_stock":
      return "text-slate-400 bg-slate-400/10 border-slate-400/20";
  }
}
