import { useQuery } from "@tanstack/react-query"
import { Bot, Cpu, DollarSign, Gauge, Timer } from "lucide-react"
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { ChartContainer, ChartGrid, chartColors } from "@/components/shared/charts"
import { Skeleton } from "@/components/ui/skeleton"
import { formatCurrency, formatDuration, formatPercent } from "@/lib/utils"
import type { AgentAnalytics, ModelStats, ProviderPerformance } from "@/types/api"

const piePalette = [chartColors.cyan, chartColors.violet, chartColors.magenta, chartColors.green, chartColors.amber]

export function AnalyticsPage() {
  const agentStats = useQuery({
    queryKey: ["analytics", "agents"],
    queryFn: () => feClient.get<AgentAnalytics[]>("/optimization/agents"),
    refetchInterval: 30_000,
  })
  const providerPerf = useQuery({
    queryKey: ["analytics", "providers"],
    queryFn: () => feClient.get<ProviderPerformance[]>("/optimization/routing/performance"),
    refetchInterval: 30_000,
  })
  const modelStats = useQuery({
    queryKey: ["analytics", "models"],
    queryFn: () => feClient.get<ModelStats>("/governance/models/stats"),
    refetchInterval: 30_000,
  })

  const agents = agentStats.data ?? []
  const providers = providerPerf.data ?? []
  const stats = modelStats.data

  const tokenTrend = Object.entries(stats?.providers ?? {}).map(([provider, p]) => ({
    label: provider === "" ? "default" : provider,
    input: Math.round((p.tokens ?? 0) / 2),
    output: Math.round((p.tokens ?? 0) / 2),
  }))
  const costTrend = Object.entries(stats?.providers ?? {}).map(([provider, p]) => ({
    label: provider === "" ? "default" : provider,
    cost: p.cost_usd ?? 0,
  }))

  if (agentStats.isPending || providerPerf.isPending || modelStats.isPending) return <AnalyticsSkeleton />
  if (agentStats.isError || providerPerf.isError || modelStats.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message={agentStats.error?.message ?? providerPerf.error?.message} onRetry={() => agentStats.refetch()} />
      </div>
    )
  }

  const totalCalls = providers.reduce((acc, p) => acc + p.total_calls, 0)
  const avgLatency = agents.length
    ? agents.reduce((acc, a) => acc + a.average_latency_ms, 0) / agents.length
    : 0

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Analytics"
        description="Model, agent and provider performance telemetry."
        eyebrow="Intelligence"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Agent runs" value={agents.reduce((a, x) => a + x.total_runs, 0)} icon={Bot} accent="primary" hint="all agents" />
        <StatCard label="API calls" value={stats?.total_requests ?? totalCalls} icon={Cpu} accent="accent" hint="across providers" />
        <StatCard label="Avg latency" value={formatDuration(avgLatency)} icon={Timer} accent="warning" hint="per agent" />
        <StatCard label="Learned ranking" value={providers.length} icon={Gauge} accent="success" hint="providers ranked" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <CardShell title="Token consumption" description="Token share by provider" action={<span className="text-xs tabular-nums text-muted-foreground">{stats?.total_tokens.toLocaleString() ?? 0} total</span>}>
          {tokenTrend.length ? (
            <div className="h-[280px]">
              <ChartContainer>
                <BarChart data={tokenTrend}>
                  <ChartGrid />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} width={40} tick={{ fontSize: 12 }} allowDecimals={false} />
                  <Bar dataKey="input" name="Input" fill={chartColors.cyan} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="output" name="Output" fill={chartColors.violet} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ChartContainer>
            </div>
          ) : (
            <EmptyState title="No token data" description="Token usage will be tracked here as AI calls are made." className="h-[280px]" />
          )}
        </CardShell>

        <CardShell title="Cost by provider" description="Spend in USD" action={<span className="text-xs tabular-nums text-muted-foreground">{formatCurrency(stats?.total_cost_usd ?? 0)} total</span>}>
          {costTrend.length ? (
            <div className="h-[280px]">
              <ChartContainer>
                <LineChart data={costTrend}>
                  <ChartGrid />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} width={40} tick={{ fontSize: 12 }} />
                  <Line type="monotone" dataKey="cost" name="Cost" stroke={chartColors.amber} strokeWidth={2} dot={false} />
                </LineChart>
              </ChartContainer>
            </div>
          ) : (
            <EmptyState title="No cost data" description="Spend will be tracked here as AI calls are made." className="h-[280px]" />
          )}
        </CardShell>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <CardShell title="Provider performance" description="Success rate by provider">
          <ProviderTable providers={providers} />
        </CardShell>
        <CardShell title="Agent success rate" description="Agent-level reliability">
          <AgentBars agents={agents} spend={stats?.total_cost_usd ?? 0} />
        </CardShell>
      </div>
    </div>
  )
}

function ProviderTable({ providers }: { providers: ProviderPerformance[] }) {
  if (!providers.length)
    return (
      <EmptyState title="No provider performance data" description="Provider routing stats will appear here." className="min-h-[200px]" />
    )
  return (
    <div className="space-y-3">
      {providers.map((p) => (
        <div key={p.provider} className="rounded-lg border p-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium capitalize">{p.provider}</p>
            <span className="text-xs tabular-nums text-emerald-500">{formatPercent(p.success_rate / 100)}</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
            <div className="h-full rounded-full bg-emerald-500/80" style={{ width: `${p.success_rate}%` }} />
          </div>
          <div className="mt-2 flex justify-between text-xs text-muted-foreground">
            <span>{p.total_calls} calls</span>
            <span className="tabular-nums">{formatDuration(p.average_latency_ms)} avg</span>
          </div>
        </div>
      ))}
    </div>
  )
}

function AgentBars({ agents, spend }: { agents: AgentAnalytics[]; spend: number }) {
  if (!agents.length)
    return (
      <EmptyState title="No agent analytics" description="Agent runs will be tracked here." className="min-h-[200px]" />
    )
  return (
    <div className="space-y-3">
      {agents.map((a, i) => (
        <div key={a.agent} className="flex items-center gap-3">
          <span className="w-24 truncate text-xs font-medium capitalize">{a.agent}</span>
          <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full"
              style={{ width: `${a.success_rate}%`, backgroundColor: piePalette[i % piePalette.length] }}
            />
          </div>
          <span className="w-12 text-right text-xs tabular-nums text-muted-foreground">{a.success_rate.toFixed(0)}%</span>
        </div>
      ))}
      <div className="mt-4 flex items-center gap-3 rounded-lg border bg-muted/20 p-3">
        <DollarSign className="h-4 w-4 text-amber-500" />
        <p className="text-xs text-muted-foreground">
          <span className="font-medium text-foreground">{formatCurrency(spend)}</span> total spend this period
        </p>
      </div>
    </div>
  )
}

function AnalyticsSkeleton() {
  return (
    <div className="container px-6 py-8">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="mt-2 h-4 w-72" />
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-80" />
        <Skeleton className="h-80" />
      </div>
    </div>
  )
}