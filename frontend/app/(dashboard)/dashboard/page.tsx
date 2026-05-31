"use client";

import { motion } from "framer-motion";
import { useDashboard } from "@/hooks/useSales";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { RevenueChart } from "@/components/dashboard/RevenueChart";
import { SalesByBranch } from "@/components/dashboard/SalesByBranch";
import { TopProducts } from "@/components/dashboard/TopProducts";
import { InventoryAlerts } from "@/components/dashboard/InventoryAlerts";
import { AIInsightsPanel } from "@/components/dashboard/AIInsightsPanel";
import { formatRelativeTime } from "@/utils/formatters";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.07 } },
};

const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function DashboardPage() {
  const { data, isLoading } = useDashboard();

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header */}
      <motion.div variants={item} className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm mt-0.5">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
        {data?.lastUpdated && (
          <p className="text-xs text-slate-500">
            Updated {formatRelativeTime(data.lastUpdated)}
          </p>
        )}
      </motion.div>

      {/* KPI Grid */}
      <motion.div variants={item}>
        <KPIGrid metrics={data?.kpis} isLoading={isLoading} />
      </motion.div>

      {/* Revenue Chart + Inventory Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div variants={item} className="lg:col-span-2">
          <RevenueChart data={data?.revenueData} isLoading={isLoading} />
        </motion.div>
        <motion.div variants={item}>
          <InventoryAlerts alerts={data?.inventoryAlerts} isLoading={isLoading} />
        </motion.div>
      </div>

      {/* Sales by Branch + Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={item}>
          <SalesByBranch data={data?.salesByBranch} isLoading={isLoading} />
        </motion.div>
        <motion.div variants={item}>
          <TopProducts products={data?.topProducts} isLoading={isLoading} />
        </motion.div>
      </div>

      {/* AI Insights */}
      <motion.div variants={item}>
        <AIInsightsPanel insights={data?.aiInsights} isLoading={isLoading} />
      </motion.div>
    </motion.div>
  );
}
