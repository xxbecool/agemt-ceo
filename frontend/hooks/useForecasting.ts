"use client";

import { useQuery } from "@tanstack/react-query";
import { QUERY_KEYS } from "@/utils/constants";
import type { ForecastData, ForecastDataPoint } from "@/types/dashboard.types";
import { subDays, addDays, format } from "date-fns";

function generateForecastData(days: number): ForecastData {
  const today = new Date();
  const revenueForecast: ForecastDataPoint[] = [];

  // Historical data (past 30 days)
  for (let i = 30; i >= 1; i--) {
    const date = subDays(today, i);
    const base = 160000 + Math.random() * 80000;
    revenueForecast.push({
      date: format(date, "yyyy-MM-dd"),
      actual: Math.round(base),
      forecast: Math.round(base * (0.95 + Math.random() * 0.1)),
      upperBound: Math.round(base * 1.15),
      lowerBound: Math.round(base * 0.85),
    });
  }

  // Forecast data (future)
  const lastActual = revenueForecast[revenueForecast.length - 1].actual!;
  for (let i = 1; i <= days; i++) {
    const date = addDays(today, i);
    const growthFactor = 1 + (0.004 * i) / 30;
    const base = lastActual * growthFactor * (0.9 + Math.random() * 0.2);
    const uncertainty = 0.05 + (0.005 * i) / 30;
    revenueForecast.push({
      date: format(date, "yyyy-MM-dd"),
      forecast: Math.round(base),
      upperBound: Math.round(base * (1 + uncertainty)),
      lowerBound: Math.round(base * (1 - uncertainty)),
    });
  }

  return {
    revenueForecast,
    modelAccuracy: {
      mape: 3.2,
      rmse: 12450,
      r2Score: 0.94,
      lastTrainedAt: subDays(today, 1).toISOString(),
    },
    inventoryPredictions: [
      { productId: "p1", productName: "SSD 512GB Enterprise", currentStock: 12, predictedStockout: format(addDays(today, 3), "yyyy-MM-dd"), recommendedReorder: 200, confidence: 97 },
      { productId: "p2", productName: "RAM 32GB DDR5", currentStock: 28, predictedStockout: format(addDays(today, 5), "yyyy-MM-dd"), recommendedReorder: 300, confidence: 94 },
      { productId: "p3", productName: "Network Switch 48-Port", currentStock: 45, predictedStockout: format(addDays(today, 9), "yyyy-MM-dd"), recommendedReorder: 150, confidence: 91 },
      { productId: "p4", productName: "UPS 2000VA", currentStock: 67, predictedStockout: format(addDays(today, 14), "yyyy-MM-dd"), recommendedReorder: 200, confidence: 88 },
      { productId: "p5", productName: "Server GPU A100", currentStock: 89, predictedStockout: format(addDays(today, 21), "yyyy-MM-dd"), recommendedReorder: 100, confidence: 85 },
      { productId: "p6", productName: "Intel Xeon Platinum", currentStock: 156, predictedStockout: format(addDays(today, 32), "yyyy-MM-dd"), recommendedReorder: 120, confidence: 82 },
    ],
    forecastPeriod: days,
  };
}

export function useForecasting(period: number = 90) {
  return useQuery<ForecastData>({
    queryKey: [...QUERY_KEYS.forecasting, period],
    queryFn: async () => {
      try {
        const { default: api } = await import("@/services/api");
        const response = await api.get<ForecastData>("/forecasting", {
          params: { period },
        });
        return response.data;
      } catch {
        return generateForecastData(period);
      }
    },
    staleTime: 10 * 60 * 1000,
  });
}
