"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Package, AlertTriangle, TrendingUp, DollarSign, Warehouse } from "lucide-react";
import { useInventory } from "@/hooks/useInventory";
import { InventoryAlerts } from "@/components/dashboard/InventoryAlerts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { formatCurrency, formatNumber, formatPercentage, getStatusColor } from "@/utils/formatters";
import { CHART_COLORS } from "@/utils/constants";
import { cn } from "@/utils/cn";
import type { InventoryItem } from "@/types/dashboard.types";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

const STATUS_LABELS: Record<string, string> = {
  in_stock: "In Stock",
  low_stock: "Low Stock",
  critical: "Critical",
  out_of_stock: "Out of Stock",
};

export default function InventoryPage() {
  const { data, isLoading } = useInventory();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const filteredItems = (data?.items || []).filter((item) => {
    const matchStatus = statusFilter === "all" || item.status === statusFilter;
    const matchSearch =
      !search ||
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.sku.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const summary = data?.summary;
  const summaryCards = summary ? [
    { label: "Total Items", value: formatNumber(summary.totalItems), icon: Package, color: "text-blue-400 bg-blue-400/10" },
    { label: "Total Value", value: formatCurrency(summary.totalValue, { compact: true }), icon: DollarSign, color: "text-emerald-400 bg-emerald-400/10" },
    { label: "Low Stock", value: summary.lowStockItems.toString(), icon: AlertTriangle, color: "text-amber-400 bg-amber-400/10" },
    { label: "Avg Turnover", value: `${summary.averageTurnover}x`, icon: TrendingUp, color: "text-purple-400 bg-purple-400/10" },
  ] : [];

  const warehouseData = data?.warehouseUtilization.map((w) => ({
    name: w.warehouse.split(" ")[1] || w.warehouse,
    percentage: w.percentage,
    used: w.used,
    capacity: w.capacity,
  }));

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Summary cards */}
      <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse bg-slate-800/50 rounded-xl border border-slate-700/50" />
            ))
          : summaryCards.map((card) => {
              const Icon = card.icon;
              return (
                <Card key={card.label}>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-3 mb-2">
                      <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center", card.color)}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <p className="text-xs text-slate-400">{card.label}</p>
                    </div>
                    <p className="text-2xl font-bold text-white">{card.value}</p>
                  </CardContent>
                </Card>
              );
            })}
      </motion.div>

      {/* Alerts + Warehouse Utilization */}
      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <InventoryAlerts alerts={data?.alerts} isLoading={isLoading} maxItems={7} />

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Warehouse className="w-5 h-5 text-slate-400" />
              <div>
                <CardTitle>Warehouse Utilization</CardTitle>
                <CardDescription>Storage capacity by location</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-56 animate-pulse bg-slate-700/30 rounded-lg" />
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={warehouseData} layout="vertical" margin={{ top: 5, right: 40, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94A3B8", fontSize: 11 }} tickFormatter={(v) => `${v}%`} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: "#94A3B8", fontSize: 11 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip
                    contentStyle={{ background: "#1E293B", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }}
                    formatter={(v: number) => [`${v}%`, "Utilization"]}
                  />
                  <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
                    {warehouseData?.map((entry, idx) => (
                      <Cell
                        key={idx}
                        fill={
                          entry.percentage >= 85
                            ? CHART_COLORS.danger
                            : entry.percentage >= 70
                            ? CHART_COLORS.warning
                            : CHART_COLORS.primary
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
            <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-blue-500" /> Normal (&lt;70%)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-amber-500" /> High (70-85%)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-red-500" /> Critical (&gt;85%)</span>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Inventory Table */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>Inventory Items</CardTitle>
                <CardDescription>
                  {filteredItems.length} of {data?.items.length || 0} items
                </CardDescription>
              </div>
              <div className="flex gap-2 flex-wrap">
                <input
                  type="text"
                  placeholder="Search items..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="px-3 py-1.5 text-sm bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 w-40"
                />
                <div className="flex gap-1">
                  {["all", "critical", "low_stock", "in_stock", "out_of_stock"].map((s) => (
                    <button
                      key={s}
                      onClick={() => setStatusFilter(s)}
                      className={cn(
                        "px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors capitalize",
                        statusFilter === s ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white hover:bg-slate-700"
                      )}
                    >
                      {s === "all" ? "All" : s.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-left text-xs font-medium text-slate-400 px-6 py-3">Product</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Stock</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Value</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-4 py-3">Days on Hand</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Turnover</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-6 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading
                    ? Array.from({ length: 8 }).map((_, i) => (
                        <tr key={i} className="border-b border-slate-700/30">
                          <td colSpan={6} className="px-6 py-3">
                            <div className="h-4 animate-pulse bg-slate-700/30 rounded" />
                          </td>
                        </tr>
                      ))
                    : filteredItems.map((inv: InventoryItem) => (
                        <tr key={inv.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                          <td className="px-6 py-3">
                            <p className="font-medium text-white">{inv.name}</p>
                            <p className="text-xs text-slate-500">{inv.sku} · {inv.category} · {inv.warehouseLocation}</p>
                          </td>
                          <td className="px-4 py-3 text-right tabular-nums">
                            <span className="text-white font-medium">{inv.currentStock.toLocaleString()}</span>
                            <span className="text-slate-500 text-xs"> / {inv.reorderPoint}</span>
                          </td>
                          <td className="px-4 py-3 text-right text-slate-300 tabular-nums">
                            {formatCurrency(inv.totalValue, { compact: true })}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={cn(
                              "text-sm font-medium",
                              inv.daysOnHand === 0 ? "text-red-400" :
                              inv.daysOnHand <= 7 ? "text-red-400" :
                              inv.daysOnHand <= 21 ? "text-amber-400" : "text-slate-300"
                            )}>
                              {inv.daysOnHand === 0 ? "Out" : `${inv.daysOnHand}d`}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right text-slate-300">
                            {inv.turnoverRate}x
                          </td>
                          <td className="px-6 py-3 text-center">
                            <Badge
                              className={cn("text-xs", getStatusColor(inv.status))}
                              variant="outline"
                            >
                              {STATUS_LABELS[inv.status]}
                            </Badge>
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
