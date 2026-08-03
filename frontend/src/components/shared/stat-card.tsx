import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react"
import type { ComponentType } from "react"

import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

interface StatCardProps {
  label: string
  value: string | number
  icon: ComponentType<{ className?: string }>
  hint?: string
  trend?: number
  trendLabel?: string
  loading?: boolean
  accent?: "default" | "primary" | "success" | "destructive" | "warning" | "accent"
}

const accentMap: Record<string, string> = {
  default: "text-muted-foreground",
  primary: "text-primary",
  success: "text-emerald-500",
  destructive: "text-destructive",
  warning: "text-amber-500",
  accent: "text-violet-400",
}

const accentBg: Record<string, string> = {
  default: "bg-muted/60",
  primary: "bg-primary/10",
  success: "bg-emerald-500/10",
  destructive: "bg-destructive/10",
  warning: "bg-amber-500/10",
  accent: "bg-violet-500/10",
}

export function StatCard({
  label,
  value,
  icon: Icon,
  hint,
  trend,
  trendLabel,
  loading,
  accent = "default",
}: StatCardProps) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1.5">
            <p className="text-[13px] font-medium text-muted-foreground">{label}</p>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <p className="font-display text-2xl font-semibold tracking-tight tabular-nums">{value}</p>
            )}
          </div>
          <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg ring-1 ring-inset ring-border/40", accentMap[accent], accentBg[accent])}>
            <Icon className="h-[18px] w-[18px]" />
          </div>
        </div>
        {(trend !== undefined || hint) && (
          <div className="mt-3 flex items-center gap-2 text-xs">
            {trend !== undefined && (
              <span
                className={cn(
                  "inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 font-medium",
                  trend > 0 && "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
                  trend < 0 && "bg-red-500/10 text-red-600 dark:text-red-400",
                  trend === 0 && "bg-muted text-muted-foreground",
                )}
              >
                {trend > 0 ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : trend < 0 ? (
                  <ArrowDownRight className="h-3 w-3" />
                ) : (
                  <Minus className="h-3 w-3" />
                )}
                {Math.abs(trend)}%
              </span>
            )}
            {trendLabel && <span className="text-muted-foreground">{trendLabel}</span>}
            {!trend && <span className="text-muted-foreground">{hint}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  )
}