export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: "success" | "error";
  pagination?: PaginationMeta;
}

export interface PaginationMeta {
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}

export interface DateRange {
  from: Date;
  to: Date;
}

export type TimeRange = "7d" | "30d" | "90d" | "180d" | "1y" | "custom";

export interface QueryParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  search?: string;
  dateRange?: TimeRange;
  from?: string;
  to?: string;
}
