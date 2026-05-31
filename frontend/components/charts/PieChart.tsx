"use client";

import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { CHART_COLORS } from "@/utils/constants";

const COLORS = [
  CHART_COLORS.primary,
  CHART_COLORS.secondary,
  CHART_COLORS.success,
  CHART_COLORS.warning,
  CHART_COLORS.info,
];

interface PieChartProps {
  data: Array<{ name: string; value: number }>;
  height?: number;
  formatValue?: (v: number) => string;
}

export function PieChart({
  data,
  height = 260,
  formatValue = (v) => v.toLocaleString(),
}: PieChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: "#1E293B", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }}
          formatter={(v) => [formatValue(v as number)]}
        />
        <Legend wrapperStyle={{ fontSize: "12px", color: "#94A3B8" }} />
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}
