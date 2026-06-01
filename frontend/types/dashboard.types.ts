export interface KPIMetric {
  id: string;
  label: string;
  value: number;
  previousValue: number;
  change: number;
  changePercent: number;
  trend: "up" | "down" | "neutral";
  format: "currency" | "percentage" | "number" | "count";
  icon: string;
  color: "blue" | "green" | "amber" | "red" | "purple";
}

export interface RevenueDataPoint {
  date: string;
  revenue: number;
  target: number;
  previousYear: number;
}

export interface SalesByBranchData {
  branch: string;
  revenue: number;
  target: number;
  growth: number;
  orders: number;
}

export interface TopProduct {
  id: string;
  name: string;
  sku: string;
  category: string;
  revenue: number;
  units: number;
  growth: number;
  margin: number;
}

export interface InventoryAlert {
  id: string;
  productName: string;
  sku: string;
  currentStock: number;
  reorderPoint: number;
  category: string;
  severity: "critical" | "warning" | "info";
  daysUntilStockout: number;
  warehouseLocation: string;
}

export interface AIInsight {
  id: string;
  title: string;
  description: string;
  category: "revenue" | "inventory" | "forecast" | "risk" | "opportunity";
  priority: "high" | "medium" | "low";
  actionable: boolean;
  createdAt: string;
  metric?: {
    label: string;
    value: string;
    change: number;
  };
}

export interface DashboardData {
  kpis: KPIMetric[];
  revenueData: RevenueDataPoint[];
  salesByBranch: SalesByBranchData[];
  topProducts: TopProduct[];
  inventoryAlerts: InventoryAlert[];
  aiInsights: AIInsight[];
  lastUpdated: string;
}

export interface SalesData {
  overview: {
    totalRevenue: number;
    totalOrders: number;
    averageOrderValue: number;
    conversionRate: number;
    revenueGrowth: number;
    ordersGrowth: number;
  };
  revenueByDay: RevenueDataPoint[];
  topProducts: TopProduct[];
  salesByBranch: SalesByBranchData[];
  salesByCategory: {
    category: string;
    revenue: number;
    units: number;
    percentage: number;
  }[];
}

export interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  category: string;
  currentStock: number;
  reorderPoint: number;
  maxStock: number;
  unitCost: number;
  totalValue: number;
  supplier: string;
  warehouseLocation: string;
  lastRestocked: string;
  turnoverRate: number;
  daysOnHand: number;
  status: "in_stock" | "low_stock" | "critical" | "out_of_stock";
}

export interface WarehouseUtilization {
  warehouse: string;
  capacity: number;
  used: number;
  percentage: number;
}

export interface InventoryData {
  summary: {
    totalItems: number;
    totalValue: number;
    lowStockItems: number;
    criticalItems: number;
    outOfStockItems: number;
    averageTurnover: number;
  };
  items: InventoryItem[];
  alerts: InventoryAlert[];
  warehouseUtilization: WarehouseUtilization[];
}

export interface ForecastDataPoint {
  date: string;
  actual?: number;
  forecast: number;
  upperBound: number;
  lowerBound: number;
}

export interface ForecastData {
  revenueForecast: ForecastDataPoint[];
  modelAccuracy: {
    mape: number;
    rmse: number;
    r2Score: number;
    lastTrainedAt: string;
  };
  inventoryPredictions: {
    productId: string;
    productName: string;
    currentStock: number;
    predictedStockout: string;
    recommendedReorder: number;
    confidence: number;
  }[];
  forecastPeriod: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}
