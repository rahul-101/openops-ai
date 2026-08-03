import { CloudCog, Gauge, Timer, XCircle } from "lucide-react"

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from "recharts"

import { PageHeader } from "@/components/shared/page-header"
import { StatCard } from "@/components/shared/stat-card"
import { CardShell } from "@/components/shared/card-shell"
import {
  ChartContainer,
  ChartGrid,
  chartColors,
} from "@/components/shared/charts"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { ActivityFeed } from "./activity-feed"
import { useDashboardSnapshot, useOperationsEvents } from "./hooks"
import { formatDuration, formatPercent } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Reveal, StaggerGroup, StaggerItem } from "@/components/shared/motion"
import type { OperationsEvent } from "@/types/api"

const piePalette = [
  chartColors.cyan,
  chartColors.violet,
  chartColors.magenta,
  chartColors.green,
  chartColors.amber,
]

export function DashboardPage() {
  const snapshot = useDashboardSnapshot()
  const events = useOperationsEvents(100)

  if (snapshot.isPending) {
    return <DashboardSkeleton />
  }
  if (snapshot.isError) {
    return (
      <div className="container px-6 py-8">
        <ErrorState message={snapshot.error.message} onRetry={() => snapshot.refetch()} />
      </div>
    )
  }

  const data = snapshot.data!
  const liveEvents = events.data ?? []
  const modelData = Object.entries(data.ai.model_usage ?? {}).map(([name, value]) => ({
    name: name === "" ? "default" : name,
    value,
  }))

  const activityTrend = bucketByHour(liveEvents)
  const outcomeTrend = bucketOutcomes(liveEvents)
  const agentRates = agentSuccessRates(liveEvents)

  return (
    <div className="mx-auto w-full max-w-[1440px] px-6 py-8">
      <PageHeader
        title="Operations Dashboard"
        description="Live view of autonomous incident response across your environment."
        eyebrow="Overview"
      />

      <StaggerGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StaggerItem>
          <StatCard label="Total Incidents" value={data.incidents.total_incidents} icon={Gauge} accent="primary" hint="all time" />
        </StaggerItem>
        <StaggerItem>
          <StatCard label="Open Incidents" value={data.incidents.open_incidents} icon={Timer} accent="warning" hint="needs attention" />
        </StaggerItem>
        <StaggerItem>
          <StatCard label="Auto-resolution" value={formatPercent(data.incidents.auto_resolution_rate)} icon={CloudCog} accent="success" trendLabel="autonomous" />
        </StaggerItem>
        <StaggerItem>
          <StatCard label="Avg resolution" value={formatDuration(data.incidents.average_resolution_time_s * 1000)} icon={XCircle} accent="accent" hint="per incident" />
        </StaggerItem>
      </StaggerGroup>

      <Reveal>
        <div className="mt-4 grid gap-4 lg:grid-cols-6">
        <CardShell title="Agent execution activity" description="Execution events over time" className="lg:col-span-4" action={<Badge variant="secondary">{formatTokenCount(data.ai.input_tokens)} in · {formatTokenCount(data.ai.output_tokens)} out</Badge>}>
          {activityTrend.length ? (
            <div className="h-[280px]">
              <ChartContainer>
                <AreaChart data={activityTrend}>
                  <defs>
                    <linearGradient id="gTokens" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={chartColors.cyan} stopOpacity={0.4} />
                      <stop offset="95%" stopColor={chartColors.cyan} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <ChartGrid />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} width={40} tick={{ fontSize: 12 }} allowDecimals={false} />
                  <Area type="monotone" dataKey="count" name="Events" stroke={chartColors.cyan} strokeWidth={2} fill="url(#gTokens)" />
                </AreaChart>
              </ChartContainer>
            </div>
          ) : (
            <EmptyState
              title="No activity yet"
              description="Ingest an alert and run a lifecycle to see live execution activity here."
              className="h-[280px]"
            />
          )}
        </CardShell>

        <CardShell title="Model usage" description="Share of requests by model" className="lg:col-span-2">
          {modelData.length ? (
            <div className="h-[280px]">
              <ChartContainer>
                <PieChart>
                  <Pie data={modelData} dataKey="value" nameKey="name" innerRadius={62} outerRadius={92} paddingAngle={3}>
                    {modelData.map((_, i) => (
                      <Cell key={i} fill={piePalette[i % piePalette.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ChartContainer>
              <div className="mt-2 flex flex-wrap justify-center gap-x-4 gap-y-1">
                {modelData.map((m, i) => (
                  <span key={m.name} className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: piePalette[i % piePalette.length] }} />
                    {m.name}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState
              title="No model usage yet"
              description="Model attribution will appear as AI calls are tracked."
              className="h-[280px]"
            />
          )}
        </CardShell>
      </div>
      </Reveal>

      <Reveal>
      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <CardShell title="Execution outcomes" description="Succeeded vs failed remediation actions" className="lg:col-span-2">
          {outcomeTrend.length ? (
            <div className="h-[220px]">
              <ChartContainer>
                <BarChart data={outcomeTrend}>
                  <ChartGrid />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} width={40} tick={{ fontSize: 12 }} allowDecimals={false} />
                  <Bar dataKey="success" name="Succeeded" fill={chartColors.green} radius={[4, 4, 0, 0]} stackId="a" />
                  <Bar dataKey="failed" name="Failed" fill={chartColors.magenta} radius={[4, 4, 0, 0]} stackId="a" />
                </BarChart>
              </ChartContainer>
            </div>
          ) : (
            <EmptyState
              title="No executions yet"
              description="Risk-gated tool executions will show up here."
              className="h-[220px]"
            />
          )}
        </CardShell>

        <CardShell title="Agent success rate" description="Runs across agents">
          <div className="space-y-3">
            {agentRates.length ? (
              agentRates.map((a) => (
                <div key={a.agent} className="flex items-center gap-3">
                  <span className="w-28 truncate text-xs font-medium capitalize">{a.agent}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-emerald-500/80" style={{ width: `${a.rate * 100}%` }} />
                  </div>
                  <span className="w-12 text-right text-xs tabular-nums text-muted-foreground">{formatPercent(a.rate, 0)}</span>
                </div>
              ))
            ) : (
              <EmptyState
                title="No agent runs"
                description="Agent executions will appear here in real time."
                className="min-h-[160px]"
              />
            )}
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">Total agent runs</p>
              <p className="mt-1 text-xl font-semibold tabular-nums">{data.ai.total_agent_runs}</p>
            </div>
          </div>
        </CardShell>
      </div>
      </Reveal>

      <Reveal>
      <div className="mt-4">
        <ActivityFeed />
      </div>
      </Reveal>
      <div className="h-10" />
    </div>
  )
}

function bucketByHour(events: OperationsEvent[]) {
  if (!events.length) return []
  const buckets = new Map<string, number>()
  for (const e of events) {
    const key = new Date(e.timestamp)
    if (isNaN(key.getTime())) continue
    key.setMinutes(0, 0, 0)
    buckets.set(key.toISOString(), (buckets.get(key.toISOString()) ?? 0) + 1)
  }
  return [...buckets.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([iso, count]) => ({ label: new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), count }))
}

function bucketOutcomes(events: OperationsEvent[]) {
  const buckets = new Map<string, { label: string; success: number; failed: number }>()
  for (const e of events) {
    if (e.category !== "execution" || e.type !== "tool_execution_completed") continue
    const key = new Date(e.timestamp)
    if (isNaN(key.getTime())) continue
    key.setMinutes(0, 0, 0)
    const iso = key.toISOString()
    const bucket = buckets.get(iso) ?? {
      label: key.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      success: 0,
      failed: 0,
    }
    if (e.status === "success") bucket.success += 1
    else if (e.status === "failure") bucket.failed += 1
    buckets.set(iso, bucket)
  }
  return [...buckets.values()].sort((a, b) => a.label.localeCompare(b.label))
}

function agentSuccessRates(events: OperationsEvent[]) {
  const totals = new Map<string, { success: number; total: number }>()
  for (const e of events) {
    if (e.category !== "execution" || e.type !== "tool_execution_completed" || !e.agent) continue
    const entry = totals.get(e.agent) ?? { success: 0, total: 0 }
    entry.total += 1
    if (e.status === "success") entry.success += 1
    totals.set(e.agent, entry)
  }
  return [...totals.entries()]
    .map(([agent, { success, total }]) => ({ agent, rate: total ? success / total : 0 }))
    .sort((a, b) => b.rate - a.rate)
}

function formatTokenCount(value: number): string {
  return new Intl.NumberFormat(undefined).format(value)
}

function DashboardSkeleton() {
  return (
    <div className="mx-auto w-full max-w-[1440px] px-6 py-8">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
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