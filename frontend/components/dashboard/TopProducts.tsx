"use client";

import { TrendingUp, TrendingDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatPercentage } from "@/utils/formatters";
import type { TopProduct } from "@/types/dashboard.types";
import { TableSkeleton } from "@/components/shared/LoadingSkeleton";
import { cn } from "@/utils/cn";

interface TopProductsProps {
  products?: TopProduct[];
  isLoading?: boolean;
}

export function TopProducts({ products, isLoading }: TopProductsProps) {
  if (isLoading) return <TableSkeleton rows={5} />;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Products</CardTitle>
        <CardDescription>By revenue this period</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left text-xs font-medium text-slate-400 px-6 py-3">Product</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Revenue</th>
                <th className="text-right text-xs font-medium text-slate-400 px-4 py-3">Units</th>
                <th className="text-right text-xs font-medium text-slate-400 px-6 py-3">Growth</th>
              </tr>
            </thead>
            <tbody>
              {products?.map((product, i) => (
                <tr
                  key={product.id}
                  className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors"
                >
                  <td className="px-6 py-3">
                    <div>
                      <p className="font-medium text-white truncate max-w-[180px]">{product.name}</p>
                      <p className="text-xs text-slate-500">{product.sku} · {product.category}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-semibold text-white tabular-nums">
                      {formatCurrency(product.revenue, { compact: true })}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className="text-slate-300 tabular-nums">
                      {product.units.toLocaleString()}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <div className={cn(
                      "inline-flex items-center gap-1 text-sm font-semibold",
                      product.growth >= 0 ? "text-emerald-400" : "text-red-400"
                    )}>
                      {product.growth >= 0 ? (
                        <TrendingUp className="w-3.5 h-3.5" />
                      ) : (
                        <TrendingDown className="w-3.5 h-3.5" />
                      )}
                      {formatPercentage(Math.abs(product.growth))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
