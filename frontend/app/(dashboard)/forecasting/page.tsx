"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Brain, TrendingUp, Target, AlertCircle, Calendar } from "lucide-react";
import { useForecasting } from "@/hooks/useForecasting";
import { ForecastChart } from "@/components/charts/ForecastChart";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FORECAST_PERIODS } from "@/utils/constants";
import { formatCurrency, formatDate, formatPercentage } from "@/utils/formatters";
import { cn } from "@/utils/cn";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function ForecastingPage() {
  const [period, setPeriod] = useState(90);
  const { data, isLoading } = useForecasting(period);

  const accuracy = data?.modelAccuracy;

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Header with period selector */}
      <motion.div variants={item} className="flex items-center justify-between flex-wrap gap-3">
        <p className="text-slate-400 text-sm">AI-powered revenue and inventory predictions</p>
        <div className="flex gap-1.5 bg-slate-800/80 rounded-lg p-1">
          {FORECAST_PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={cn(
                "px-3 py-1.5 text-xs font-medium rounded-md transition-all",
                period === p.value
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-white hover:bg-slate-700"
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Model Accuracy Cards */}
      <motion.div variants={item} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse bg-slate-800/50 rounded-xl border border-slate-700/50" />
            ))
          : [
              {
                label: "Model Accuracy (R²)",
                value: accuracy ? `${(accuracy.r2Score * 100).toFixed(1)}%` : "N/A",
                sub: "Coefficient of determination",
                icon: Brain,
                color: "text-blue-400 bg-blue-400/10",
                good: true,
              },
              {
                label: "MAPE",
                value: accuracy ? `${accuracy.mape}%` : "N/A",
                sub: "Mean absolute percentage error",
                icon: Target,
                color: "text-emerald-400 bg-emerald-400/10",
                good: true,
              },
              {
                label: "RMSE",
                value: accuracy ? formatCurrency(accuracy.rmse, { compact: true }) : "N/A",
                sub: "Root mean square error",
                icon: TrendingUp,
                color: "text-amber-400 bg-amber-400/10",
                good: false,
              },
              {
                label: "Last Trained",
                value: accuracy ? formatDate(accuracy.lastTrainedAt, "MMM dd") : "N/A",
                sub: "Model freshness",
                icon: Calendar,
                color: "text-purple-400 bg-purple-400/10",
                good: true,
              },
            ].map((card) => {
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
                    <p className="text-xl font-bold text-white">{card.value}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{card.sub}</p>
                  </CardContent>
                </Card>
              );
            })}
      </motion.div>

      {/* Forecast Chart */}
      <motion.div variants={item}>
        <ForecastChart data={data?.revenueForecast} isLoading={isLoading} />
      </motion.div>

      {/* Inventory Depletion Predictions */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-400" />
              <div>
                <CardTitle>Inventory Depletion Predictions</CardTitle>
                <CardDescription>AI-predicted stockout dates and reorder recommendations</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-left text-xs font-medium text-slate-400 px-6 py-3">Product</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Current Stock</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-4 py-3">Predicted Stockout</th>
                    <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Reorder Qty</th>
                    <th className="text-center text-xs font-medium text-slate-400 px-6 py-3">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {isLoading
                    ? Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b border-slate-700/30">
                          <td colSpan={5} className="px-6 py-3">
                            <div className="h-4 animate-pulse bg-slate-700/30 rounded" />
                          </td>
                        </tr>
                      ))
                    : data?.inventoryPredictions.map((pred) => {
                        const stockoutDate = new Date(pred.predictedStockout);
                        const daysUntil = Math.round((stockoutDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
                        const isUrgent = daysUntil <= 7;
                        const isWarning = daysUntil <= 21;

                        return (
                          <tr key={pred.productId} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                            <td className="px-6 py-3">
                              <p className="font-medium text-white">{pred.productName}</p>
                              <p className="text-xs text-slate-500">ID: {pred.productId}</p>
                            </td>
                            <td className="px-4 py-3 text-right text-slate-300 tabular-nums">
                              {pred.currentStock.toLocaleString()} units
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className={cn(
                                "text-sm font-medium",
                                isUrgent ? "text-red-400" : isWarning ? "text-amber-400" : "text-slate-300"
                              )}>
                                {formatDate(pred.predictedStockout, "MMM dd, yyyy")}
                              </span>
                              <p className="text-xs text-slate-500">{daysUntil} days remaining</p>
                            </td>
                            <td className="px-4 py-3 text-right font-semibold text-white tabular-nums">
                              {pred.recommendedReorder.toLocaleString()} units
                            </td>
                            <td className="px-6 py-3 text-center">
                              <div className="flex items-center justify-center gap-2">
                                <div className="w-24 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                                  <div
                                    className={cn("h-full rounded-full", pred.confidence >= 90 ? "bg-emerald-500" : pred.confidence >= 80 ? "bg-amber-500" : "bg-red-500")}
                                    style={{ width: `${pred.confidence}%` }}
                                  />
                                </div>
                                <span className={cn(
                                  "text-xs font-semibold",
                                  pred.confidence >= 90 ? "text-emerald-400" : pred.confidence >= 80 ? "text-amber-400" : "text-red-400"
                                )}>
                                  {pred.confidence}%
                                </span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
