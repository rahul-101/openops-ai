import { useQuery } from "@tanstack/react-query"
import { Cpu, DollarSign, Gauge, Server } from "lucide-react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { cn, formatNumber, formatPercent, formatCurrency, formatDuration, formatDateTime, titleCase } from "@/lib/utils"
import type { ProviderMetadata } from "@/types/api"

interface AuditLogEntry {
  id: string
  timestamp: string
  user: string
  action: string
  decision: string
  incident_id?: string | null
  agent?: string | null
  model?: string | null
}

const RISK_COLORS: Record<string, string> = {
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-600",
  high: "border-destructive/30 bg-destructive/10 text-destructive",
}

const DECISION_STYLES: Record<string, string> = {
  approved: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  executed: "border-sky-500/30 bg-sky-500/10 text-sky-600",
  rejected: "border-destructive/30 bg-destructive/10 text-destructive",
  pending: "border-amber-500/30 bg-amber-500/10 text-amber-600",
}

export function ModelGovernancePage() {
  const providers = useQuery({
    queryKey: ["providers"],
    queryFn: () => feClient.get<ProviderMetadata[]>("/providers"),
  })
  const modelStats = useQuery({
    queryKey: ["modelStats"],
    queryFn: () => feClient.get<any>("/governance/models/stats"),
  })
  const policyActions = useQuery({
    queryKey: ["policyActions"],
    queryFn: () => feClient.get<Record<string, string>>("/governance/approval-policy/actions"),
  })
  const auditLogs = useQuery({
    queryKey: ["auditLogs"],
    queryFn: () => feClient.get<AuditLogEntry[]>("/governance/audit"),
  })
  if (providers.isPending || modelStats.isPending || policyActions.isPending) {
    return <ModelGovernanceSkeleton />
  }
  if (providers.isError || modelStats.isError || policyActions.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message="Failed to load governance data" onRetry={() => window.location.reload()} />
      </div>
    )
  }

  const totalProviders = providers.data?.length ?? 0
  const stats = modelStats.data ?? { total_requests: 0, total_tokens: 0, total_cost_usd: 0, average_latency_ms: 0, providers: {} }
  const policy = policyActions.data ?? {}

  return (
    <div className="mx-auto w-full max-w-[1600px] px-6 py-8">
      <PageHeader
        title="Model Governance"
        description="Manage AI model providers, usage patterns and compliance policies."
        eyebrow="Governance"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Providers"
          value={totalProviders}
          icon={Server}
          accent="primary"
          hint="registered"
        />
        <StatCard
          label="Model Requests"
          value={formatNumber(stats.total_requests)}
          icon={Cpu}
          accent="accent"
          hint="all time"
        />
        <StatCard
          label="Model Costs"
          value={formatCurrency(stats.total_cost_usd)}
          icon={DollarSign}
          accent="warning"
          hint="current month"
        />
        <StatCard
          label="Avg Latency"
          value={formatDuration(stats.average_latency_ms * 1000)}
          icon={Gauge}
          accent="success"
          hint="per request"
        />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <CardShell
          title="Model Usage Stats"
          description="Token consumption, costs and performance metrics"
          className="lg:col-span-2"
        >
          {stats.providers && Object.keys(stats.providers).length > 0 ? (
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                {Object.entries(stats.providers).map(([provider, data]: [string, any]) => (
                  <div key={provider} className="rounded-lg border p-4">
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">{provider}</p>
                        <p className="text-xs text-muted-foreground">{formatNumber(data.requests)} requests</p>
                      </div>
                      <Badge variant="outline" className={cn("px-2 py-0.5 text-[10px]", RISK_COLORS.low)}>{formatPercent((data.cost_usd / stats.total_cost_usd * 100) || 0, 1)}%</Badge>
                    </div>
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Cost</span>
                        <span>{formatCurrency(data.cost_usd)}</span>
                      </div>
                      <Progress value={((data.cost_usd / stats.total_cost_usd) * 100) || 0} className="mt-1" />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                      <span>Tokens</span>
                      <span>{formatNumber(data.tokens)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState
              title="No model usage yet"
              description="Model usage tracking will appear as AI calls are made."
              className="min-h-[240px]"
            />
          )}
        </CardShell>

        <CardShell
          title="Action Risk Policy"
          description="Registered actions and their risk levels"
        >
          {policy && Object.keys(policy).length > 0 ? (
            <div className="divide-y rounded-lg border">
              {Object.entries(policy).map(([action, risk]) => (
                <div key={action} className="flex items-center justify-between px-3 py-2">
                  <span className="font-mono text-xs">{action}</span>
                  <Badge variant="outline" className={cn("px-2 py-0.5 text-[10px]", RISK_COLORS[risk] ?? "bg-muted text-muted-foreground")}>
                    {risk}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No policy data"
              description="Risk policy will appear once actions are registered."
              className="min-h-[160px]"
            />
          )}
        </CardShell>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <CardShell
          title="Provider Registry"
          description="Active AI model providers and their status"
        >
          {providers.data?.length ? (
            <div className="space-y-2">
              {providers.data.map((p) => (
                <div key={p.name} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{p.display_name ?? titleCase(p.name)}</p>
                    <p className="truncate font-mono text-xs text-muted-foreground">{p.model}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={p.enabled ? "default" : "secondary"}>{p.enabled ? "Enabled" : "Disabled"}</Badge>
                    <Badge variant="outline">#{p.priority}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No providers configured"
              description="AI providers will appear here once configured."
              className="min-h-[160px]"
            />
          )}
        </CardShell>

        <CardShell
          title="Recent Governance Activity"
          description="Latest audit events and policy decisions"
        >
          {auditLogs.data && auditLogs.data.length > 0 ? (
            <div className="space-y-2">
              {auditLogs.data.slice(0, 5).map((log) => (
                <div key={log.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{log.action}</p>
                    <p className="truncate text-xs text-muted-foreground">{log.user} • {formatDateTime(log.timestamp)}</p>
                  </div>
                  <Badge variant="outline" className={cn("px-2 py-0.5 text-[10px]", DECISION_STYLES[log.decision] ?? "bg-muted text-muted-foreground")}>{titleCase(log.decision || "recorded")}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No governance activity"
              description="Audit logs will appear as governance actions occur."
              className="min-h-[160px]"
            />
          )}
        </CardShell>
      </div>
    </div>
  )
}

function ModelGovernanceSkeleton() {
  return (
    <div className="container px-6 py-8">
      <div className="space-y-2">
        <Skeleton className="h-8 w-56" />
        <Skeleton className="h-4 w-72" />
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Skeleton className="h-80 lg:col-span-2" />
        <Skeleton className="h-80" />
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
    </div>
  )
}
