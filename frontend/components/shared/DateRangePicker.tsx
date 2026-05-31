"use client";

import { Calendar, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { TimeRange } from "@/types/api.types";
import { TIME_RANGES } from "@/utils/constants";

interface DateRangePickerProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
  className?: string;
}

export function DateRangePicker({ value, onChange, className }: DateRangePickerProps) {
  const selectedLabel = TIME_RANGES.find((r) => r.value === value)?.label || "30 Days";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className={className}>
          <Calendar className="w-4 h-4 mr-2" />
          {selectedLabel}
          <ChevronDown className="w-4 h-4 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {TIME_RANGES.filter((r) => r.value !== "custom").map((range) => (
          <DropdownMenuItem
            key={range.value}
            onClick={() => onChange(range.value as TimeRange)}
            className={value === range.value ? "bg-slate-700 text-white" : ""}
          >
            {range.label}
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={() => onChange("custom")}
          className={value === "custom" ? "bg-slate-700 text-white" : ""}
        >
          Custom Range
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
