import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { IncidentSeverity, IncidentStatus } from "@/types/api"

const severityStyles: Record<IncidentSeverity, string> = {
  CRITICAL: "border-transparent bg-destructive/15 text-red-600 dark:text-red-400",
  HIGH: "border-transparent bg-orange-500/15 text-orange-600 dark:text-orange-400",
  MEDIUM: "border-transparent bg-amber-500/15 text-amber-600 dark:text-amber-400",
  LOW: "border-transparent bg-slate-500/15 text-slate-600 dark:text-slate-400",
}
const severityLabel: Record<IncidentSeverity, string> = {
  CRITICAL: "Critical",
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
}

const statusStyles: Record<IncidentStatus, string> = {
  OPEN: "border-transparent bg-sky-500/15 text-sky-600 dark:text-sky-400",
  IN_PROGRESS: "border-transparent bg-violet-500/15 text-violet-600 dark:text-violet-400",
  RESOLVED: "border-transparent bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
}
const statusLabel: Record<IncidentStatus, string> = {
  OPEN: "Open",
  IN_PROGRESS: "In Progress",
  RESOLVED: "Resolved",
}

export function SeverityBadge({ severity, className }: { severity: IncidentSeverity; className?: string }) {
  return <Badge className={cn(severityStyles[severity], className)}>{severityLabel[severity]}</Badge>
}

export function StatusBadge({ status, className }: { status: IncidentStatus; className?: string }) {
  return (
    <Badge className={cn(statusStyles[status], className)}>
      <span
        className={cn(
          "mr-1.5 inline-block h-1.5 w-1.5 rounded-full",
          status === "OPEN" && "animate-pulse bg-sky-500",
          status === "IN_PROGRESS" && "animate-pulse bg-violet-500",
          status === "RESOLVED" && "bg-emerald-500",
        )}
      />
      {statusLabel[status]}
    </Badge>
  )
}

function circuitStyle(state: string): string {
  const upper = state.toUpperCase()
  if (upper === "CLOSED") return "border-transparent bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
  if (upper === "OPEN") return "border-transparent bg-destructive/15 text-red-600 dark:text-red-400"
  if (upper === "HALF_OPEN") return "border-transparent bg-amber-500/15 text-amber-600 dark:text-amber-400"
  return "border-transparent bg-secondary text-muted-foreground"
}

export function CircuitBadge({ state, className }: { state: string; className?: string }) {
  return (
    <Badge className={cn(circuitStyle(state), className)}>
      <span
        className={cn(
          "mr-1.5 inline-block h-1.5 w-1.5 rounded-full",
          state.toUpperCase() === "CLOSED" && "bg-emerald-500",
          state.toUpperCase() === "OPEN" && "animate-pulse bg-red-500",
          state.toUpperCase() === "HALF_OPEN" && "animate-pulse bg-amber-500",
        )}
      />
      {state.replaceAll("_", " ").toLowerCase()}
    </Badge>
  )
}

export { severityStyles, statusStyles }