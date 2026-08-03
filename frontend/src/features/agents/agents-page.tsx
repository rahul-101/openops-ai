import { Bot, Cpu, Gauge, Timer } from "lucide-react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { useAgentAnalytics, useAgentSummary } from "./hooks"
import { formatDuration } from "@/lib/utils"

const agentPalette = ["#22d3ee", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b"]

export function AgentsPage() {
  const analytics = useAgentAnalytics()
  const summary = useAgentSummary()

  if (analytics.isPending || summary.isPending) return <AgentsSkeleton />
  if (analytics.isError || summary.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message={analytics.error?.message ?? summary.error?.message} onRetry={() => analytics.refetch()} />
      </div>
    )
  }

  const agents = analytics.data ?? []

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Agents"
        description="The fleet of specialized AI agents that power autonomous incident response."
        eyebrow="Automation"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total agents" value={summary.data?.total_agents ?? agents.length} icon={Bot} accent="primary" hint="registered" />
        <StatCard label="Total runs" value={summary.data?.total_runs ?? "—"} icon={Cpu} accent="accent" hint="all time" />
        <StatCard label="Success rate" value={formatSuccess(summary.data?.overall_success_rate)} icon={Gauge} accent="success" hint="across agents" />
        <StatCard label="Avg latency" value={formatDuration(avgLatency(agents))} icon={Timer} accent="warning" hint="per run" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {agents.length === 0 && (
          <div className="lg:col-span-2">
            <CardShell title="Agent fleet">
              <EmptyState
                title="No agents registered yet"
                description="Agent analytics will appear as agents execute workflows."
              />
            </CardShell>
          </div>
        )}
        {agents.map((agent, i) => {
          const successRate = agent.success_rate
          return (
            <CardShell key={agent.agent} title={agent.agent} action={<Badge variant="outline">{formatSuccess(successRate)}</Badge>}>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span
                    className="flex h-10 w-10 items-center justify-center rounded-lg text-white"
                    style={{ backgroundColor: agentPalette[i % agentPalette.length] }}
                  >
                    <Bot className="h-5 w-5" />
                  </span>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Success rate</span>
                      <span className="font-medium tabular-nums">{formatSuccess(successRate)}</span>
                    </div>
                    <Progress value={successRate} className="h-1.5" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-lg font-semibold tabular-nums">{agent.total_runs}</p>
                    <p className="text-[11px] text-muted-foreground">Total runs</p>
                  </div>
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-lg font-semibold tabular-nums">{agent.failed_runs}</p>
                    <p className="text-[11px] text-muted-foreground">Failed</p>
                  </div>
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-lg font-semibold tabular-nums">{formatDuration(agent.average_latency_ms)}</p>
                    <p className="text-[11px] text-muted-foreground">Avg latency</p>
                  </div>
                </div>
              </div>
            </CardShell>
          )
        })}
      </div>
    </div>
  )
}

function formatSuccess(value: number | undefined): string {
  if (value === undefined) return "—"
  return `${value.toFixed(0)}%`
}

function avgLatency(agents: { average_latency_ms: number }[]): number {
  if (!agents.length) return 0
  return agents.reduce((acc, a) => acc + a.average_latency_ms, 0) / agents.length
}

function AgentsSkeleton() {
  return (
    <div className="container px-6 py-8">
      <div className="space-y-2">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-4 w-80" />
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-44" />
        ))}
      </div>
    </div>
  )
}