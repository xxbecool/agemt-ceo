"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatCurrency } from "@/utils/formatters";
import { CHART_COLORS } from "@/utils/constants";
import type { SalesByBranchData } from "@/types/dashboard.types";
import { ChartSkeleton } from "@/components/shared/LoadingSkeleton";

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-white mb-2">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2 text-sm">
          <span className="w-2 h-2 rounded-sm" style={{ background: entry.color }} />
          <span className="text-slate-400">{entry.name}:</span>
          <span className="text-white font-semibold">{formatCurrency(entry.value, { compact: true })}</span>
        </div>
      ))}
    </div>
  );
}

interface SalesByBranchProps {
  data?: SalesByBranchData[];
  isLoading?: boolean;
}

export function SalesByBranch({ data, isLoading }: SalesByBranchProps) {
  if (isLoading) return <ChartSkeleton height={280} />;

  const formattedData = data?.map((d) => ({ ...d, branch: d.branch.split(" ")[0] }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sales by Branch</CardTitle>
        <CardDescription>Revenue vs target by location</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={formattedData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
            <XAxis dataKey="branch" tick={{ fill: "#94A3B8", fontSize: 11 }} axisLine={{ stroke: CHART_COLORS.grid }} tickLine={false} />
            <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatCurrency(v, { compact: true })} width={65} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: "12px", fontSize: "12px", color: "#94A3B8" }} />
            <Bar dataKey="target" name="Target" fill={CHART_COLORS.muted} opacity={0.4} radius={[2, 2, 0, 0]} />
            <Bar dataKey="revenue" name="Revenue" fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
