"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, ShoppingCart, DollarSign, BarChart3, Percent } from "lucide-react";
import { useSales } from "@/hooks/useSales";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { DateRangePicker } from "@/components/shared/DateRangePicker";
import { RevenueChart } from "@/components/dashboard/RevenueChart";
import { SalesByBranch } from "@/components/dashboard/SalesByBranch";
import { PieChart } from "@/components/charts/PieChart";
import { formatCurrency, formatNumber, formatPercentage } from "@/utils/formatters";
import { cn } from "@/utils/cn";
import type { TimeRange } from "@/types/api.types";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function SalesPage() {
  const [dateRange, setDateRange] = useState<TimeRange>("30d");
  const { data, isLoading } = useSales(dateRange);

  const overviewCards = data ? [
    { label: "Total Revenue", value: formatCurrency(data.overview.totalRevenue, { compact: true }), change: data.overview.revenueGrowth, icon: DollarSign, color: "blue" },
    { label: "Total Orders", value: formatNumber(data.overview.totalOrders, { compact: true }), change: data.overview.ordersGrowth, icon: ShoppingCart, color: "purple" },
    { label: "Avg Order Value", value: formatCurrency(data.overview.averageOrderValue), change: 3.2, icon: BarChart3, color: "green" },
    { label: "Conversion Rate", value: formatPercentage(data.overview.conversionRate), change: 0.4, icon: Percent, color: "amber" },
  ] : [];

  const COLOR_MAP: Record<string, string> = {
    blue: "bg-blue-500/20 text-blue-400",
    purple: "bg-purple-500/20 text-purple-400",
    green: "bg-emerald-500/20 text-emerald-400",
    amber: "bg-amber-500/20 text-amber-400",
  };

  const categoryPieData = data?.salesByCategory.map((c) => ({
    name: c.category,
    value: c.revenue,
  })) || [];

  const [sortBy, setSortBy] = useState<"revenue" | "units" | "growth">("revenue");
  const sortedProducts = [...(data?.topProducts || [])].sort((a, b) => b[sortBy] - a[sortBy]);

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex items-center justify-between">
        <p className="text-slate-400 text-sm">Revenue, orders, and performance metrics</p>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-28 animate-pulse bg-slate-800/50 rounded-xl border border-slate-700/50" />
            ))
          : overviewCards.map((card) => {
              const Icon = card.icon;
              return (
                <Card key={card.label}>
                  <CardContent className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm text-slate-400">{card.label}</p>
                      <div className={cn("w-9 h-9 rounded-lg flex items-center justify-center", COLOR_MAP[card.color])}>
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-white mb-1">{card.value}</p>
                    <div className={cn("flex items-center gap-1 text-sm font-semibold", card.change >= 0 ? "text-emerald-400" : "text-red-400")}>
                      {card.change >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                      {formatPercentage(Math.abs(card.change))}
                      <span className="text-slate-500 font-normal text-xs">vs prior period</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
      </motion.div>

      <motion.div variants={item}>
        <RevenueChart data={data?.revenueByDay} isLoading={isLoading} />
      </motion.div>

      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SalesByBranch data={data?.salesByBranch} isLoading={isLoading} />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Category</CardTitle>
            <CardDescription>Product category breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <PieChart data={categoryPieData} height={220} formatValue={(v) => formatCurrency(v, { compact: true })} />
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div>
                <CardTitle>Product Performance</CardTitle>
                <CardDescription>All products sorted by selected metric</CardDescription>
              </div>
              <div className="flex gap-1">
                {(["revenue", "units", "growth"] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => setSortBy(s)}
                    className={cn(
                      "px-3 py-1.5 text-xs font-medium rounded-md transition-colors capitalize",
                      sortBy === s ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white hover:bg-slate-700"
                    )}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-left text-xs font-medium text-slate-400 px-6 py-3">Product</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Revenue</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Units</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Growth</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-6 py-3">Margin</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading
                    ? Array.from({ length: 6 }).map((_, i) => (
                        <tr key={i} className="border-b border-slate-700/30">
                          <td colSpan={5} className="px-6 py-3">
                            <div className="h-4 animate-pulse bg-slate-700/30 rounded" />
                          </td>
                        </tr>
                      ))
                    : sortedProducts.map((p) => (
                        <tr key={p.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                          <td className="px-6 py-3">
                            <p className="font-medium text-white">{p.name}</p>
                            <p className="text-xs text-slate-500">{p.sku} · {p.category}</p>
                          </td>
                          <td className="px-4 py-3 text-right font-semibold text-white tabular-nums">
                            {formatCurrency(p.revenue, { compact: true })}
                          </td>
                          <td className="px-4 py-3 text-right text-slate-300 tabular-nums">
                            {p.units.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className={cn("font-semibold", p.growth >= 0 ? "text-emerald-400" : "text-red-400")}>
                              {p.growth >= 0 ? "+" : ""}{formatPercentage(p.growth)}
                            </span>
                          </td>
                          <td className="px-6 py-3 text-right text-slate-300">
                            {formatPercentage(p.margin)}
                          </td>
                        </tr>
                      ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
