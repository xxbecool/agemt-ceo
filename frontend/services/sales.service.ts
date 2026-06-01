import api from "./api";
import type { SalesData, DashboardData } from "@/types/dashboard.types";
import type { QueryParams } from "@/types/api.types";
import { subDays, format } from "date-fns";

function generateRevenueData(days: number) {
  const data = [];
  const today = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const date = subDays(today, i);
    const base = 180000 + Math.random() * 80000;
    const target = 200000;
    const prevYear = base * (0.8 + Math.random() * 0.15);
    data.push({
      date: format(date, "yyyy-MM-dd"),
      revenue: Math.round(base),
      target,
      previousYear: Math.round(prevYear),
    });
  }
  return data;
}

const mockSalesData: SalesData = {
  overview: {
    totalRevenue: 4_823_156,
    totalOrders: 18_432,
    averageOrderValue: 261.7,
    conversionRate: 3.8,
    revenueGrowth: 12.4,
    ordersGrowth: 8.2,
  },
  revenueByDay: generateRevenueData(30),
  topProducts: [
    { id: "p1", name: "Enterprise Suite Pro", sku: "ESP-001", category: "Software", revenue: 924500, units: 312, growth: 18.2, margin: 72.4 },
    { id: "p2", name: "Analytics Dashboard", sku: "AD-002", category: "Software", revenue: 756200, units: 891, growth: 14.7, margin: 68.1 },
    { id: "p3", name: "Cloud Storage 1TB", sku: "CS-003", category: "Infrastructure", revenue: 534100, units: 2145, growth: 9.3, margin: 54.2 },
    { id: "p4", name: "Security Firewall", sku: "SF-004", category: "Security", revenue: 445800, units: 187, growth: 22.1, margin: 61.8 },
    { id: "p5", name: "API Gateway", sku: "AG-005", category: "Infrastructure", revenue: 389300, units: 423, growth: -2.4, margin: 58.9 },
    { id: "p6", name: "ML Pipeline Tool", sku: "ML-006", category: "AI/ML", revenue: 312400, units: 98, growth: 34.5, margin: 76.2 },
    { id: "p7", name: "DevOps Toolkit", sku: "DT-007", category: "Software", revenue: 278900, units: 543, growth: 6.8, margin: 63.5 },
    { id: "p8", name: "Database Pro", sku: "DB-008", category: "Database", revenue: 245600, units: 312, growth: 11.2, margin: 59.7 },
  ],
  salesByBranch: [
    { branch: "New York HQ", revenue: 1_245_800, target: 1_200_000, growth: 15.2, orders: 4821 },
    { branch: "San Francisco", revenue: 987_400, target: 1_000_000, growth: 8.7, orders: 3654 },
    { branch: "London", revenue: 876_500, target: 850_000, growth: 12.1, orders: 3201 },
    { branch: "Singapore", revenue: 654_300, target: 700_000, growth: -2.3, orders: 2456 },
    { branch: "Chicago", revenue: 543_200, target: 500_000, growth: 18.4, orders: 2103 },
    { branch: "Berlin", revenue: 432_100, target: 450_000, growth: 5.6, orders: 1876 },
    { branch: "Sydney", revenue: 356_800, target: 380_000, growth: -4.1, orders: 1543 },
    { branch: "Toronto", revenue: 287_400, target: 280_000, growth: 9.2, orders: 1234 },
  ],
  salesByCategory: [
    { category: "Software", revenue: 2_123_456, units: 8921, percentage: 44.0 },
    { category: "Infrastructure", revenue: 1_234_567, units: 5432, percentage: 25.6 },
    { category: "Security", revenue: 876_543, units: 2341, percentage: 18.2 },
    { category: "AI/ML", revenue: 589_012, units: 987, percentage: 12.2 },
  ],
};

export const salesService = {
  async getSalesData(params?: QueryParams): Promise<SalesData> {
    try {
      const response = await api.get<SalesData>("/sales", { params });
      return response.data;
    } catch {
      const days = params?.dateRange === "7d" ? 7 : params?.dateRange === "90d" ? 90 : 30;
      return { ...mockSalesData, revenueByDay: generateRevenueData(days) };
    }
  },

  async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await api.get<DashboardData>("/dashboard");
      return response.data;
    } catch {
      return {
        kpis: [
          { id: "revenue", label: "Total Revenue", value: 4_823_156, previousValue: 4_290_123, change: 533033, changePercent: 12.4, trend: "up", format: "currency", icon: "DollarSign", color: "blue" },
          { id: "growth", label: "Month Growth", value: 12.4, previousValue: 9.8, change: 2.6, changePercent: 26.5, trend: "up", format: "percentage", icon: "TrendingUp", color: "green" },
          { id: "alerts", label: "Active Alerts", value: 7, previousValue: 12, change: -5, changePercent: -41.7, trend: "down", format: "count", icon: "AlertTriangle", color: "amber" },
          { id: "inventory", label: "Inventory Health", value: 87.3, previousValue: 82.1, change: 5.2, changePercent: 6.3, trend: "up", format: "percentage", icon: "Package", color: "green" },
        ],
        revenueData: generateRevenueData(30),
        salesByBranch: mockSalesData.salesByBranch,
        topProducts: mockSalesData.topProducts.slice(0, 5),
        inventoryAlerts: [
          { id: "a1", productName: "SSD 512GB Enterprise", sku: "SSD-512E", currentStock: 12, reorderPoint: 50, category: "Storage", severity: "critical", daysUntilStockout: 3, warehouseLocation: "WH-A" },
          { id: "a2", productName: "RAM 32GB DDR5", sku: "RAM-32G", currentStock: 28, reorderPoint: 75, category: "Memory", severity: "critical", daysUntilStockout: 5, warehouseLocation: "WH-B" },
          { id: "a3", productName: "Network Switch 48-Port", sku: "NS-48P", currentStock: 45, reorderPoint: 100, category: "Networking", severity: "warning", daysUntilStockout: 9, warehouseLocation: "WH-A" },
          { id: "a4", productName: "UPS 2000VA", sku: "UPS-2K", currentStock: 67, reorderPoint: 120, category: "Power", severity: "warning", daysUntilStockout: 14, warehouseLocation: "WH-C" },
          { id: "a5", productName: "Server GPU A100", sku: "GPU-A100", currentStock: 89, reorderPoint: 150, category: "GPU", severity: "info", daysUntilStockout: 21, warehouseLocation: "WH-B" },
        ],
        aiInsights: [
          { id: "i1", title: "Revenue Acceleration Detected", description: "Revenue growth has increased by 12.4% this month, outpacing the 9.8% target. New York HQ and Chicago branches are driving above-target performance with strong enterprise software sales.", category: "revenue", priority: "high", actionable: true, createdAt: new Date().toISOString(), metric: { label: "Revenue Growth", value: "+12.4%", change: 26.5 } },
          { id: "i2", title: "Critical Inventory Risk: 2 SKUs", description: "SSD-512E and RAM-32G are at critical stockout risk within 3-5 days. Immediate reorder recommended. Estimated lost revenue if stockout occurs: $234,500.", category: "inventory", priority: "high", actionable: true, createdAt: new Date().toISOString(), metric: { label: "At-Risk Revenue", value: "$234K", change: -100 } },
          { id: "i3", title: "Q4 Forecast Looks Promising", description: "Based on current trajectory and seasonal patterns, Q4 revenue is projected at $5.8M — 8.2% above the $5.36M target. ML Pipeline and Security products show strongest momentum.", category: "forecast", priority: "medium", actionable: false, createdAt: new Date().toISOString(), metric: { label: "Q4 Projection", value: "$5.8M", change: 8.2 } },
          { id: "i4", title: "Singapore Branch Underperforming", description: "Singapore is tracking 6.8% below its monthly target. The gap has widened over 3 consecutive months. Consider reviewing pricing strategy and local sales team performance.", category: "risk", priority: "medium", actionable: true, createdAt: new Date().toISOString(), metric: { label: "Target Gap", value: "-6.8%", change: -6.8 } },
        ],
        lastUpdated: new Date().toISOString(),
      };
    }
  },
};
