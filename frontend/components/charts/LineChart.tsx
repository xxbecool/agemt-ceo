"use client";

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { CHART_COLORS } from "@/utils/constants";

interface LineConfig {
  key: string;
  color: string;
  label?: string;
  dashed?: boolean;
}

interface LineChartProps {
  data: Array<Record<string, string | number>>;
  lines: LineConfig[];
  xKey?: string;
  height?: number;
  formatValue?: (v: number) => string;
}

export function LineChart({
  data,
  lines,
  xKey = "date",
  height = 250,
  formatValue = (v) => v.toLocaleString(),
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
        <XAxis dataKey={xKey} tick={{ fill: "#94A3B8", fontSize: 10 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: "#94A3B8", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={formatValue} width={60} />
        <Tooltip
          contentStyle={{ background: "#1E293B", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }}
          formatter={(v) => [formatValue(v as number)]}
        />
        <Legend wrapperStyle={{ fontSize: "12px", color: "#94A3B8" }} />
        {lines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            name={line.label || line.key}
            stroke={line.color}
            strokeWidth={2}
            strokeDasharray={line.dashed ? "4 4" : undefined}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}
