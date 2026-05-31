import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-blue-600/20 text-blue-400 border-blue-500/30",
        secondary:
          "border-transparent bg-slate-700 text-slate-300",
        destructive:
          "border-transparent bg-red-600/20 text-red-400 border-red-500/30",
        outline: "text-slate-400 border-slate-600",
        success:
          "border-transparent bg-emerald-600/20 text-emerald-400 border-emerald-500/30",
        warning:
          "border-transparent bg-amber-600/20 text-amber-400 border-amber-500/30",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
