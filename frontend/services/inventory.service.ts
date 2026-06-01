import api from "./api";
import type { InventoryData } from "@/types/dashboard.types";
import type { QueryParams } from "@/types/api.types";

const mockInventoryData: InventoryData = {
  summary: {
    totalItems: 1_247,
    totalValue: 8_934_567,
    lowStockItems: 34,
    criticalItems: 7,
    outOfStockItems: 3,
    averageTurnover: 6.2,
  },
  items: [
    { id: "i1", name: "SSD 512GB Enterprise", sku: "SSD-512E", category: "Storage", currentStock: 12, reorderPoint: 50, maxStock: 200, unitCost: 189.99, totalValue: 2279.88, supplier: "Samsung Enterprise", warehouseLocation: "WH-A Row 12", lastRestocked: "2025-04-01", turnoverRate: 18.4, daysOnHand: 3, status: "critical" },
    { id: "i2", name: "RAM 32GB DDR5", sku: "RAM-32G", category: "Memory", currentStock: 28, reorderPoint: 75, maxStock: 300, unitCost: 124.99, totalValue: 3499.72, supplier: "Crucial", warehouseLocation: "WH-B Row 4", lastRestocked: "2025-04-03", turnoverRate: 14.2, daysOnHand: 5, status: "critical" },
    { id: "i3", name: "Network Switch 48-Port", sku: "NS-48P", category: "Networking", currentStock: 45, reorderPoint: 100, maxStock: 400, unitCost: 2499.00, totalValue: 112455.00, supplier: "Cisco", warehouseLocation: "WH-A Row 7", lastRestocked: "2025-03-28", turnoverRate: 8.7, daysOnHand: 9, status: "low_stock" },
    { id: "i4", name: "UPS 2000VA", sku: "UPS-2K", category: "Power", currentStock: 67, reorderPoint: 120, maxStock: 500, unitCost: 899.99, totalValue: 60299.33, supplier: "APC", warehouseLocation: "WH-C Row 2", lastRestocked: "2025-03-25", turnoverRate: 5.3, daysOnHand: 14, status: "low_stock" },
    { id: "i5", name: "Server GPU A100", sku: "GPU-A100", category: "GPU", currentStock: 89, reorderPoint: 150, maxStock: 600, unitCost: 14999.00, totalValue: 1334911.00, supplier: "NVIDIA", warehouseLocation: "WH-B Row 1", lastRestocked: "2025-03-20", turnoverRate: 4.1, daysOnHand: 21, status: "low_stock" },
    { id: "i6", name: "Intel Xeon Platinum", sku: "CPU-XP8", category: "CPU", currentStock: 156, reorderPoint: 100, maxStock: 400, unitCost: 4299.00, totalValue: 670644.00, supplier: "Intel", warehouseLocation: "WH-A Row 3", lastRestocked: "2025-04-08", turnoverRate: 6.8, daysOnHand: 32, status: "in_stock" },
    { id: "i7", name: "10GbE Network Card", sku: "NIC-10G", category: "Networking", currentStock: 234, reorderPoint: 80, maxStock: 500, unitCost: 189.99, totalValue: 44457.66, supplier: "Intel", warehouseLocation: "WH-B Row 6", lastRestocked: "2025-04-05", turnoverRate: 9.2, daysOnHand: 28, status: "in_stock" },
    { id: "i8", name: "Power Supply 1200W", sku: "PSU-1200", category: "Power", currentStock: 189, reorderPoint: 60, maxStock: 400, unitCost: 299.99, totalValue: 56698.11, supplier: "Corsair", warehouseLocation: "WH-C Row 5", lastRestocked: "2025-04-02", turnoverRate: 7.4, daysOnHand: 35, status: "in_stock" },
    { id: "i9", name: "Fiber Optic Cable 100m", sku: "FOC-100", category: "Cabling", currentStock: 0, reorderPoint: 50, maxStock: 300, unitCost: 45.99, totalValue: 0, supplier: "CommScope", warehouseLocation: "WH-A Row 15", lastRestocked: "2025-03-01", turnoverRate: 12.1, daysOnHand: 0, status: "out_of_stock" },
    { id: "i10", name: "KVM Switch 8-Port", sku: "KVM-8P", category: "Networking", currentStock: 0, reorderPoint: 25, maxStock: 150, unitCost: 389.99, totalValue: 0, supplier: "Raritan", warehouseLocation: "WH-B Row 9", lastRestocked: "2025-02-28", turnoverRate: 3.8, daysOnHand: 0, status: "out_of_stock" },
  ],
  alerts: [
    { id: "a1", productName: "SSD 512GB Enterprise", sku: "SSD-512E", currentStock: 12, reorderPoint: 50, category: "Storage", severity: "critical", daysUntilStockout: 3, warehouseLocation: "WH-A" },
    { id: "a2", productName: "RAM 32GB DDR5", sku: "RAM-32G", currentStock: 28, reorderPoint: 75, category: "Memory", severity: "critical", daysUntilStockout: 5, warehouseLocation: "WH-B" },
    { id: "a3", productName: "Fiber Optic Cable 100m", sku: "FOC-100", currentStock: 0, reorderPoint: 50, category: "Cabling", severity: "critical", daysUntilStockout: 0, warehouseLocation: "WH-A" },
    { id: "a4", productName: "KVM Switch 8-Port", sku: "KVM-8P", currentStock: 0, reorderPoint: 25, category: "Networking", severity: "critical", daysUntilStockout: 0, warehouseLocation: "WH-B" },
    { id: "a5", productName: "Network Switch 48-Port", sku: "NS-48P", currentStock: 45, reorderPoint: 100, category: "Networking", severity: "warning", daysUntilStockout: 9, warehouseLocation: "WH-A" },
    { id: "a6", productName: "UPS 2000VA", sku: "UPS-2K", currentStock: 67, reorderPoint: 120, category: "Power", severity: "warning", daysUntilStockout: 14, warehouseLocation: "WH-C" },
    { id: "a7", productName: "Server GPU A100", sku: "GPU-A100", currentStock: 89, reorderPoint: 150, category: "GPU", severity: "warning", daysUntilStockout: 21, warehouseLocation: "WH-B" },
  ],
  warehouseUtilization: [
    { warehouse: "Warehouse A (New York)", capacity: 10000, used: 7842, percentage: 78.4 },
    { warehouse: "Warehouse B (Chicago)", capacity: 8000, used: 5234, percentage: 65.4 },
    { warehouse: "Warehouse C (Los Angeles)", capacity: 6000, used: 4891, percentage: 81.5 },
    { warehouse: "Warehouse D (Seattle)", capacity: 5000, used: 2134, percentage: 42.7 },
    { warehouse: "Warehouse E (Dallas)", capacity: 7500, used: 6234, percentage: 83.1 },
  ],
};

export const inventoryService = {
  async getInventoryData(params?: QueryParams): Promise<InventoryData> {
    try {
      const response = await api.get<InventoryData>("/inventory", { params });
      return response.data;
    } catch {
      return mockInventoryData;
    }
  },

  async getInventoryAlerts() {
    try {
      const response = await api.get("/inventory/alerts");
      return response.data;
    } catch {
      return mockInventoryData.alerts;
    }
  },
};
