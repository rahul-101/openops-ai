import { useQuery } from "@tanstack/react-query"
import { Activity, Gauge, Server, ShieldAlert } from "lucide-react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState } from "@/components/shared/states"
import { CircuitBadge } from "@/components/shared/status-badges"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { formatRelativeTime } from "@/lib/utils"
import type { ProviderHealth } from "@/types/api"

export function SystemHealthPage() {
  const health = useQuery({
    queryKey: ["health", "providers"],
    queryFn: () => feClient.get<ProviderHealth[]>("/ai/providers/health"),
    refetchInterval: 15_000,
  })

  if (health.isPending) return <HealthSkeleton />
  if (health.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message={health.error.message} onRetry={() => health.refetch()} />
      </div>
    )
  }

  const providers = health.data ?? []
  const healthy = providers.filter((p) => p.circuit_state?.toUpperCase() === "CLOSED").length
  const open = providers.filter((p) => p.circuit_state?.toUpperCase() === "OPEN").length

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="System Health"
        description="AI provider health, circuit breakers and failure resilience."
        eyebrow="Platform"
        action={<Badge variant="outline" className="gap-1.5"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />Live</Badge>}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Providers" value={providers.length} icon={Server} accent="primary" hint="monitored" />
        <StatCard label="Healthy" value={healthy} icon={Gauge} accent="success" hint="circuits closed" />
        <StatCard label="Circuit open" value={open} icon={ShieldAlert} accent="destructive" hint="failover active" />
        <StatCard label="Half-open" value={providers.filter((p) => p.circuit_state?.toUpperCase() === "HALF_OPEN").length} icon={Activity} accent="warning" hint="probing" />
      </div>

      <div className="mt-4">
        <CardShell title="Provider health" description="Circuit breaker state and failure telemetry">
          <div className="grid gap-3 lg:grid-cols-2">
            {providers.length === 0 && (
              <p className="text-sm text-muted-foreground">No provider health data yet.</p>
            )}
            {providers.map((p) => (
              <div key={p.provider} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <p className="font-medium capitalize">{p.provider}</p>
                  <CircuitBadge state={p.circuit_state} />
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                  <div className="rounded-md bg-muted/40 p-2.5">
                    <p className="text-muted-foreground">Consecutive failures</p>
                    <p className="mt-0.5 text-base font-semibold tabular-nums">{p.consecutive_failures}</p>
                  </div>
                  <div className="rounded-md bg-muted/40 p-2.5">
                    <p className="text-muted-foreground">Consecutive successes</p>
                    <p className="mt-0.5 text-base font-semibold tabular-nums">{p.consecutive_successes}</p>
                  </div>
                </div>
                <div className="mt-3 space-y-1 text-xs text-muted-foreground">
                  <div className="flex justify-between">
                    <span>Last success</span>
                    <span className="tabular-nums">{formatRelativeTime(p.last_success)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Last failure</span>
                    <span className="tabular-nums">{formatRelativeTime(p.last_failure)}</span>
                  </div>
                </div>
                {p.last_error && (
                  <p className="mt-2 rounded-md bg-destructive/10 p-2 text-xs text-red-500">
                    {p.last_error}
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardShell>
      </div>
    </div>
  )
}

function HealthSkeleton() {
  return (
    <div className="container px-6 py-8">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="mt-2 h-4 w-64" />
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-44" />
        ))}
      </div>
    </div>
  )
}