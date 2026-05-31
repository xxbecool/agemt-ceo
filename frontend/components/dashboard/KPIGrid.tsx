import { KPICard } from "./KPICard";
import { KPICardSkeleton } from "@/components/shared/LoadingSkeleton";
import type { KPIMetric } from "@/types/dashboard.types";

interface KPIGridProps {
  metrics?: KPIMetric[];
  isLoading?: boolean;
}

export function KPIGrid({ metrics, isLoading }: KPIGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <KPICardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!metrics?.length) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, index) => (
        <KPICard key={metric.id} metric={metric} index={index} />
      ))}
    </div>
  );
}
