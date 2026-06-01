"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Lightbulb, AlertTriangle, BarChart3, Package } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/utils/cn";
import type { AIInsight } from "@/types/dashboard.types";

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  revenue: TrendingUp,
  inventory: Package,
  forecast: BarChart3,
  risk: AlertTriangle,
  opportunity: Lightbulb,
};

const CATEGORY_COLORS: Record<string, string> = {
  revenue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
  inventory: "text-amber-400 bg-amber-400/10 border-amber-400/20",
  forecast: "text-purple-400 bg-purple-400/10 border-purple-400/20",
  risk: "text-red-400 bg-red-400/10 border-red-400/20",
  opportunity: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
};

interface AIInsightsPanelProps {
  insights?: AIInsight[];
  isLoading?: boolean;
}

export function AIInsightsPanel({ insights, isLoading }: AIInsightsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-md flex items-center justify-center">
            <span className="text-xs text-white font-bold">AI</span>
          </div>
          <div>
            <CardTitle>AI Insights</CardTitle>
            <CardDescription>Automated analysis and recommendations</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse h-24 rounded-lg bg-slate-700/30" />
            ))}
          </div>
        ) : (
          insights?.map((insight, index) => {
            const Icon = CATEGORY_ICONS[insight.category] || Lightbulb;
            const colorClass = CATEGORY_COLORS[insight.category] || CATEGORY_COLORS.opportunity;
            const isPositiveMetric = (insight.metric?.change ?? 0) >= 0;

            return (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg border border-slate-700/30 bg-slate-700/10 hover:bg-slate-700/20 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className={cn("w-8 h-8 rounded-lg border flex-shrink-0 flex items-center justify-center mt-0.5", colorClass)}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                      <h4 className="text-sm font-semibold text-white">{insight.title}</h4>
                      <Badge
                        variant={insight.priority === "high" ? "destructive" : insight.priority === "medium" ? "warning" : "secondary"}
                        className="text-[10px] py-0"
                      >
                        {insight.priority}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{insight.description}</p>
                    {insight.metric && (
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs text-slate-500">{insight.metric.label}:</span>
                        <span className={cn("text-xs font-semibold flex items-center gap-1", isPositiveMetric ? "text-emerald-400" : "text-red-400")}>
                          {isPositiveMetric ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                          {insight.metric.value}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
