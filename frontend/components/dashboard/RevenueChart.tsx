"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatCurrency, formatDateShort } from "@/utils/formatters";
import { CHART_COLORS } from "@/utils/constants";
import type { RevenueDataPoint } from "@/types/dashboard.types";
import { ChartSkeleton } from "@/components/shared/LoadingSkeleton";

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-slate-400 mb-2">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-slate-400 capitalize">{entry.name}:</span>
          <span className="text-white font-semibold">{formatCurrency(entry.value, { compact: true })}</span>
        </div>
      ))}
    </div>
  );
}

interface RevenueChartProps {
  data?: RevenueDataPoint[];
  isLoading?: boolean;
}

export function RevenueChart({ data, isLoading }: RevenueChartProps) {
  if (isLoading) return <ChartSkeleton height={280} />;

  const formattedData = data?.map((d) => ({
    ...d,
    date: formatDateShort(d.date),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue Trend</CardTitle>
        <CardDescription>Daily revenue vs target and prior year</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={formattedData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="targetGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.muted} stopOpacity={0.2} />
                <stop offset="95%" stopColor={CHART_COLORS.muted} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="prevYearGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.secondary} stopOpacity={0.2} />
                <stop offset="95%" stopColor={CHART_COLORS.secondary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
            <XAxis dataKey="date" tick={{ fill: "#94A3B8", fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} tickLine={false} interval="preserveStartEnd" />
            <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatCurrency(v, { compact: true })} width={65} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: "12px", fontSize: "12px", color: "#94A3B8" }} />
            <Area type="monotone" dataKey="previousYear" name="Prior Year" stroke={CHART_COLORS.secondary} strokeWidth={1.5} fill="url(#prevYearGrad)" strokeDasharray="4 4" dot={false} />
            <Area type="monotone" dataKey="target" name="Target" stroke={CHART_COLORS.muted} strokeWidth={1.5} fill="url(#targetGrad)" strokeDasharray="4 4" dot={false} />
            <Area type="monotone" dataKey="revenue" name="Revenue" stroke={CHART_COLORS.primary} strokeWidth={2} fill="url(#revenueGrad)" dot={false} activeDot={{ r: 4, fill: CHART_COLORS.primary }} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
