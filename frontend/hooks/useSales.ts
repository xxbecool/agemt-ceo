"use client";

import { useQuery } from "@tanstack/react-query";
import { salesService } from "@/services/sales.service";
import { QUERY_KEYS } from "@/utils/constants";
import type { TimeRange } from "@/types/api.types";

export function useDashboard() {
  return useQuery({
    queryKey: QUERY_KEYS.dashboard,
    queryFn: () => salesService.getDashboardData(),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useSales(dateRange: TimeRange = "30d") {
  return useQuery({
    queryKey: [...QUERY_KEYS.sales, dateRange],
    queryFn: () => salesService.getSalesData({ dateRange }),
    staleTime: 5 * 60 * 1000,
  });
}
