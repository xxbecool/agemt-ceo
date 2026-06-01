"use client";

import { useQuery } from "@tanstack/react-query";
import { inventoryService } from "@/services/inventory.service";
import { QUERY_KEYS } from "@/utils/constants";
import type { QueryParams } from "@/types/api.types";

export function useInventory(params?: QueryParams) {
  return useQuery({
    queryKey: [...QUERY_KEYS.inventory, params],
    queryFn: () => inventoryService.getInventoryData(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useInventoryAlerts() {
  return useQuery({
    queryKey: QUERY_KEYS.inventoryAlerts,
    queryFn: () => inventoryService.getInventoryAlerts(),
    staleTime: 2 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}
