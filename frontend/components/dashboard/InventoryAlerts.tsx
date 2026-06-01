"use client";

import { AlertTriangle, Clock, MapPin } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { InventoryAlert } from "@/types/dashboard.types";
import { cn } from "@/utils/cn";

interface InventoryAlertsProps {
  alerts?: InventoryAlert[];
  isLoading?: boolean;
  maxItems?: number;
}

export function InventoryAlerts({ alerts, isLoading, maxItems = 5 }: InventoryAlertsProps) {
  const displayAlerts = alerts?.slice(0, maxItems);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Inventory Alerts</CardTitle>
            <CardDescription>Items requiring immediate attention</CardDescription>
          </div>
          {alerts && alerts.length > 0 && (
            <div className="flex items-center gap-1.5 text-amber-400 bg-amber-400/10 border border-amber-400/20 rounded-lg px-2.5 py-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span className="text-xs font-semibold">{alerts.length} alerts</span>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="animate-pulse h-16 rounded-lg bg-slate-700/30" />
            ))}
          </div>
        ) : displayAlerts?.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-sm text-slate-400">No active alerts</p>
          </div>
        ) : (
          displayAlerts?.map((alert) => (
            <div
              key={alert.id}
              className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/20 border border-slate-700/30 hover:border-slate-600/50 transition-colors"
            >
              <div className={cn(
                "flex-shrink-0 w-2 h-2 rounded-full",
                alert.severity === "critical" ? "bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.8)]" :
                alert.severity === "warning" ? "bg-amber-500" : "bg-blue-500"
              )} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <p className="text-sm font-medium text-white truncate">{alert.productName}</p>
                  <Badge
                    variant={alert.severity === "critical" ? "destructive" : alert.severity === "warning" ? "warning" : "default"}
                    className="text-xs py-0 flex-shrink-0"
                  >
                    {alert.severity}
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span>{alert.sku}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {alert.daysUntilStockout === 0 ? "Out of stock" : `${alert.daysUntilStockout}d remaining`}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {alert.warehouseLocation}
                  </span>
                </div>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-semibold text-white">{alert.currentStock}</p>
                <p className="text-xs text-slate-400">/ {alert.reorderPoint} min</p>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
