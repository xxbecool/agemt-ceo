"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  DollarSign,
  Package,
  AlertTriangle,
  BarChart3,
  Users,
  ShoppingCart,
  Target,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { formatKPIValue, formatPercentage } from "@/utils/formatters";
import type { KPIMetric } from "@/types/dashboard.types";

const ICON_MAP: Record<string, React.ElementType> = {
  DollarSign,
  Package,
  AlertTriangle,
  BarChart3,
  TrendingUp,
  Users,
  ShoppingCart,
  Target,
};

const COLOR_MAP: Record<string, string> = {
  blue: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  green: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  amber: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  red: "bg-red-500/20 text-red-400 border-red-500/30",
  purple: "bg-purple-500/20 text-purple-400 border-purple-500/30",
};

function useAnimatedNumber(target: number, duration: number = 1200) {
  const [current, setCurrent] = useState(0);
  const startTime = useRef<number | null>(null);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    startTime.current = null;
    const animate = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCurrent(target * eased);
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [target, duration]);

  return current;
}

interface KPICardProps {
  metric: KPIMetric;
  index?: number;
}

export function KPICard({ metric, index = 0 }: KPICardProps) {
  const animatedValue = useAnimatedNumber(metric.value);
  const Icon = ICON_MAP[metric.icon] || DollarSign;
  const iconColorClass = COLOR_MAP[metric.color] || COLOR_MAP.blue;

  const isPositive = metric.changePercent > 0;
  const isNegative = metric.changePercent < 0;
  const isNeutral = metric.changePercent === 0;

  // For alerts, DOWN is good; for most others, UP is good
  const isGoodTrend =
    metric.id === "alerts"
      ? metric.trend === "down"
      : metric.trend === "up";

  const trendColor = isNeutral
    ? "text-slate-400"
    : isGoodTrend
    ? "text-emerald-400"
    : "text-red-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className="relative rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm p-5 overflow-hidden hover:border-slate-600/50 transition-all duration-300 group"
    >
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent to-slate-900/20 pointer-events-none" />

      <div className="relative flex items-start justify-between mb-3">
        <p className="text-sm font-medium text-slate-400">{metric.label}</p>
        <div className={cn("w-9 h-9 rounded-lg border flex items-center justify-center", iconColorClass)}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="relative">
        <p className="text-2xl font-bold text-white mb-2 tabular-nums">
          {formatKPIValue(animatedValue, metric.format)}
        </p>

        <div className="flex items-center gap-1.5">
          {isPositive ? (
            <TrendingUp className={cn("w-4 h-4", trendColor)} />
          ) : isNegative ? (
            <TrendingDown className={cn("w-4 h-4", trendColor)} />
          ) : (
            <Minus className="w-4 h-4 text-slate-400" />
          )}
          <span className={cn("text-sm font-semibold", trendColor)}>
            {formatPercentage(Math.abs(metric.changePercent), { showSign: false })}
          </span>
          <span className="text-xs text-slate-500">vs last period</span>
        </div>
      </div>
    </motion.div>
  );
}
