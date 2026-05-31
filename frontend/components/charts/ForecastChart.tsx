"use client";

import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { formatCurrency, formatDateShort } from "@/utils/formatters";
import { CHART_COLORS } from "@/utils/constants";
import type { ForecastDataPoint } from "@/types/dashboard.types";
import { format } from "date-fns";

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
        entry.value && (
          <div key={entry.name} className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
            <span className="text-slate-400">{entry.name}:</span>
            <span className="text-white font-semibold">{formatCurrency(entry.value, { compact: true })}</span>
          </div>
        )
      ))}
    </div>
  );
}

interface ForecastChartProps {
  data?: ForecastDataPoint[];
  isLoading?: boolean;
}

export function ForecastChart({ data, isLoading }: ForecastChartProps) {
  const today = format(new Date(), "MMM dd");

  const formattedData = data?.map((d) => ({
    ...d,
    date: formatDateShort(d.date),
    confidence: d.actual ? undefined : [d.lowerBound, d.upperBound],
  }));

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revenue Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72 animate-pulse bg-slate-700/30 rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue Forecast with Confidence Bands</CardTitle>
        <CardDescription>Historical actual vs AI-powered forecast</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={formattedData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="confidenceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.15} />
                <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} />
            <XAxis
              dataKey="date"
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              axisLine={{ stroke: CHART_COLORS.grid }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => formatCurrency(v, { compact: true })}
              width={65}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: "12px", fontSize: "12px", color: "#94A3B8" }} />
            <ReferenceLine
              x={today}
              stroke={CHART_COLORS.warning}
              strokeDasharray="4 4"
              label={{ value: "Today", fill: CHART_COLORS.warning, fontSize: 11 }}
            />
            <Area
              type="monotone"
              dataKey="upperBound"
              name="Upper Bound"
              stroke="transparent"
              fill="url(#confidenceGrad)"
              legendType="none"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              name="Lower Bound"
              stroke="transparent"
              fill="white"
              fillOpacity={0}
              legendType="none"
            />
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke={CHART_COLORS.success}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="forecast"
              name="Forecast"
              stroke={CHART_COLORS.primary}
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={false}
              activeDot={{ r: 4 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
