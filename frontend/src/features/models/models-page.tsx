import { useQuery } from "@tanstack/react-query"
import { Cpu, DollarSign, Gauge, Server } from "lucide-react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { CircuitBadge } from "@/components/shared/status-badges"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { formatNumber, titleCase } from "@/lib/utils"
import type { ProviderHealth, ProviderMetadata, ProviderMetrics } from "@/types/api"

export function ModelsPage() {
  const providers = useQuery({
    queryKey: ["models", "providers"],
    queryFn: () => feClient.get<ProviderMetadata[]>("/providers"),
  })
  const health = useQuery({
    queryKey: ["models", "health"],
    queryFn: () => feClient.get<ProviderHealth[]>("/ai/providers/health"),
    refetchInterval: 20_000,
  })
  const metrics = useQuery({
    queryKey: ["models", "metrics"],
    queryFn: () => feClient.get<ProviderMetrics[]>("/ai/providers/metrics"),
    refetchInterval: 20_000,
  })

  if (providers.isPending || health.isPending || metrics.isPending) return <ModelsSkeleton />
  if (providers.isError || health.isError || metrics.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message={providers.error?.message ?? health.error?.message} onRetry={() => providers.refetch()} />
      </div>
    )
  }

  const healthy = (health.data ?? []).filter((h) => h.circuit_state?.toUpperCase() === "CLOSED").length
  const totalCost = (metrics.data ?? []).reduce((acc, m) => acc + m.total_requests, 0)

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Model Management"
        description="AI providers, routing priority and health monitoring."
        eyebrow="Platform"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Providers" value={providers.data?.length ?? "—"} icon={Server} accent="primary" hint="registered" />
        <StatCard label="Healthy" value={healthy} icon={Gauge} accent="success" hint="circuits closed" />
        <StatCard label="Requests" value={totalCost} icon={Cpu} accent="accent" hint="all time" />
        <StatCard label="Failover rank" value={providers.data?.length ?? "—"} icon={DollarSign} accent="warning" hint="priority order" />
      </div>

      <div className="mt-4">
        <CardShell title="Provider fleet" description="Registered AI providers with metadata and health">
          <ProviderTable providers={providers.data ?? []} health={health.data ?? []} metrics={metrics.data ?? []} />
        </CardShell>
      </div>
    </div>
  )
}

function ProviderTable({
  providers,
  health,
  metrics,
}: {
  providers: ProviderMetadata[]
  health: ProviderHealth[]
  metrics: ProviderMetrics[]
}) {
  if (!providers.length)
    return (
      <EmptyState title="No providers registered" description="AI providers will appear here once configured." className="min-h-[240px]" />
    )

  const healthByProvider = Object.fromEntries(health.map((h) => [h.provider, h]))
  const metricsByProvider = Object.fromEntries(metrics.map((m) => [m.provider, m]))

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Provider</TableHead>
          <TableHead>Model</TableHead>
          <TableHead>Priority</TableHead>
          <TableHead>Circuit</TableHead>
          <TableHead>Success rate</TableHead>
          <TableHead>Avg latency</TableHead>
          <TableHead className="text-right">Enabled</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {providers.map((p) => {
          const h = healthByProvider[p.name]
          const m = metricsByProvider[p.name]
          return (
            <TableRow key={p.name}>
              <TableCell>
                <p className="font-medium">{p.display_name ?? titleCase(p.name)}</p>
                <p className="text-xs text-muted-foreground">{p.name}</p>
              </TableCell>
              <TableCell>
                <span className="font-mono text-xs">{p.model}</span>
                <p className="text-xs text-muted-foreground">{formatNumber(p.max_context_tokens)} ctx</p>
              </TableCell>
              <TableCell>
                <Badge variant="outline">#{p.priority}</Badge>
              </TableCell>
              <TableCell>{h ? <CircuitBadge state={h.circuit_state} /> : <Badge variant="outline">unknown</Badge>}</TableCell>
              <TableCell className="tabular-nums">
                {m ? `${(m.success_rate * 100).toFixed(1)}%` : "—"}
              </TableCell>
              <TableCell className="tabular-nums text-muted-foreground">
                {m ? `${m.average_response_time_ms.toFixed(0)}ms` : "—"}
              </TableCell>
              <TableCell className="text-right">
                <Switch defaultChecked={p.enabled} onCheckedChange={() => {}} aria-label={`Toggle ${p.name}`} />
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}

function ModelsSkeleton() {
  return (
    <div className="container px-6 py-8">
      <Skeleton className="h-8 w-56" />
      <Skeleton className="mt-2 h-4 w-72" />
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
      <Skeleton className="mt-4 h-96" />
    </div>
  )
}