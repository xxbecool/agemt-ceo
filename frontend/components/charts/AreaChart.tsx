"use client";

import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { CHART_COLORS } from "@/utils/constants";
import { formatCurrency } from "@/utils/formatters";

interface AreaChartProps {
  data: Array<Record<string, string | number>>;
  dataKey: string;
  xKey?: string;
  color?: string;
  height?: number;
  formatValue?: (v: number) => string;
}

export function AreaChart({
  data,
  dataKey,
  xKey = "date",
  color = CHART_COLORS.primary,
  height = 200,
  formatValue = (v) => formatCurrency(v, { compact: true }),
}: AreaChartProps) {
  const gradId = `areaGrad_${dataKey}`;
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsAreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
        <XAxis dataKey={xKey} tick={{ fill: "#94A3B8", fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: "#94A3B8", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatValue} width={60} />
        <Tooltip
          contentStyle={{ background: "#1E293B", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }}
          formatter={(v) => [formatValue(v as number), dataKey]}
        />
        <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} fill={`url(#${gradId})`} dot={false} />
      </RechartsAreaChart>
    </ResponsiveContainer>
  );
}
