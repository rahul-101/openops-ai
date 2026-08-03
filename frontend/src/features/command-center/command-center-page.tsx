import {
  Activity,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  Loader2,
  Play,
  ShieldCheck,
  XCircle,
} from "lucide-react"
import { useMemo, useState } from "react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { EmptyState } from "@/components/shared/states"
import { StaggerGroup, StaggerItem } from "@/components/shared/motion"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useSse } from "@/hooks/use-sse"
import { cn, formatDuration, formatRelativeTime, titleCase } from "@/lib/utils"
import type { OperationsEvent } from "@/types/api"
import { useOperationsEvents } from "@/features/operations/hooks"
import { RunReasoningDialog } from "./run-reasoning-dialog"
import { useReasoningHistory } from "./hooks"

const stageMeta = [
  { stage: "ingest", label: "Ingest", icon: Activity, color: "text-sky-500" },
  { stage: "analyze", label: "Analyze", icon: BrainCircuit, color: "text-violet-500" },
  { stage: "decide", label: "Decide", icon: Cpu, color: "text-fuchsia-500" },
  { stage: "execute", label: "Execute", icon: Bot, color: "text-amber-500" },
  { stage: "verify", label: "Verify", icon: ShieldCheck, color: "text-emerald-500" },
]

export function AiCommandCenterPage() {
  const events = useOperationsEvents(30)
  const history = useReasoningHistory(20)
  const [selected, setSelected] = useState<OperationsEvent | null>(null)
  const { connected } = useSse(import.meta.env.VITE_SSE_URL ?? "/api/operations/events/stream")

  const liveEvents = useMemo(() => events.data ?? [], [events.data])

  return (
    <div className="mx-auto w-full max-w-[1440px] px-6 py-8">
      <PageHeader
        title="AI Command Center"
        description="Real-time view of autonomous reasoning, tool execution and agent behavior."
        eyebrow="AI Operations"
        action={
          <Badge
            variant="secondary"
            className="gap-1.5"
          >
            <span
              className={cn(
                "inline-block h-2 w-2 rounded-full",
                connected ? "animate-pulse bg-emerald-500" : "bg-amber-500",
              )}
            />
            {connected ? "Live stream" : "Reconnecting…"}
          </Badge>
        }
      />

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-3">
          <CardShell
            title="Autonomous pipeline"
            description="Detect → Analyze → Decide → Execute → Verify"
          >
            <PipelineStages />
          </CardShell>

          <CardShell title="Reasoning history" description="Recent multi-agent reasoning runs">
            <ReasoningHistory records={history.data ?? []} loading={history.isPending} />
          </CardShell>
        </div>

        <div className="space-y-4 lg:col-span-2">
          <CardShell title="Agent execution monitor" description="Live executions and statuses">
            <AgentMonitor events={liveEvents} loading={events.isPending} selected={selected} onSelect={setSelected} />
          </CardShell>

          <CardShell title="Tool executions" description="Risk-gated remediation actions">
            <ToolExecutions events={liveEvents} loading={events.isPending} />
          </CardShell>
        </div>
      </div>
    </div>
  )
}

function PipelineStages() {
  const [active, setActive] = useState(1)
  return (
    <div className="grid grid-cols-5 gap-2">
      {stageMeta.map((stage, i) => {
        const Icon = stage.icon
        const done = i < active
        const current = i === active
        return (
          <button
            key={stage.stage}
            onClick={() => setActive(i)}
            className={cn(
              "group flex flex-col items-center gap-2 rounded-lg border p-3 text-center transition-all",
              current && "border-primary/50 bg-primary/5",
              done && !current && "hover:bg-muted/50",
            )}
            aria-current={current ? "step" : undefined}
          >
            <span
              className={cn(
                "flex h-9 w-9 items-center justify-center rounded-full border",
                done ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-500" : "border-border bg-muted/40",
                stage.color,
              )}
            >
              {done ? <CheckCircle2 className="h-4.5 w-4.5" /> : <Icon className="h-4 w-4" />}
            </span>
            <span className="text-xs font-medium">{stage.label}</span>
            {current && (
              <span className="absolute -bottom-1 h-1 w-6 rounded-full bg-primary" />
            )}
          </button>
        )
      })}
    </div>
  )
}

interface ReasoningRecord {
  incident_id: string
  confidence: number
  risk: string
  outcome: string
  agents_involved: string[]
}

function ReasoningHistory({
  records,
  loading,
}: {
  records: ReasoningRecord[]
  loading: boolean
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12" />
        ))}
      </div>
    )
  }
  if (!records.length) {
    return (
      <EmptyState
        title="No reasoning runs yet"
        description="Run an incident through the reasoning orchestrator to see decisions here."
        className="min-h-[220px]"
        action={
          <RunReasoningDialog>
            <Button size="sm">
              <Play className="mr-2 h-3.5 w-3.5" />
              Run reasoning
            </Button>
          </RunReasoningDialog>
        }
      />
    )
  }
  return (
    <StaggerGroup className="space-y-1" stagger={0.04}>
      {records.map((r) => (
        <StaggerItem key={r.incident_id}>
          <div
            className="flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/30"
          >
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-violet-500/10 text-violet-500">
              <BrainCircuit className="h-4 w-4" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">inc {r.incident_id.slice(0, 8)}</p>
              <p className="truncate text-xs text-muted-foreground">
                {(r.agents_involved ?? []).join(", ") || "no agents"}
              </p>
            </div>
            <div className="shrink-0 text-right">
              <Badge variant={r.outcome === "success" ? "outline" : "secondary"} className="mb-1">
                {titleCase(r.outcome || "pending")}
              </Badge>
              <p className="text-xs tabular-nums text-muted-foreground">{(r.confidence * 100).toFixed(0)}% conf</p>
            </div>
          </div>
        </StaggerItem>
      ))}
    </StaggerGroup>
  )
}

function AgentMonitor({
  events,
  loading,
  selected,
  onSelect,
}: {
  events: OperationsEvent[]
  loading: boolean
  selected: OperationsEvent | null
  onSelect: (e: OperationsEvent) => void
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-12" />
        ))}
      </div>
    )
  }
  const agents = Array.from(new Set(events.map((e) => e.agent).filter(Boolean)))
  const latestByAgent = agents.map((agent) => {
    const agentEvents = events.filter((e) => e.agent === agent)
    const latest = agentEvents[agentEvents.length - 1]!
    return { agent, latest }
  })

  if (!agents.length) {
    return (
      <EmptyState
        title="No agents active"
        description="Agent executions will appear here in real time."
        className="min-h-[220px]"
      />
    )
  }

  return (
    <StaggerGroup className="space-y-2" stagger={0.05}>
      {latestByAgent.map(({ agent, latest }) => (
        <StaggerItem key={agent}>
          <button
            onClick={() => onSelect(latest)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-muted/30",
              selected?.event_id === latest.event_id && "border-primary/40 bg-primary/5",
            )}
          >
            <AgentAvatar name={agent} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium capitalize">{agent}</p>
              <p className="truncate text-xs text-muted-foreground">
                {titleCase(latest.status || latest.type)}
              </p>
            </div>
            <StatusDot status={latest.status} />
          </button>
        </StaggerItem>
      ))}
    </StaggerGroup>
  )
}

function AgentAvatar({ name }: { name: string }) {
  const hue = useMemo(() => {
    let h = 0
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360
    return h
  }, [name])
  return (
    <span
      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold"
      style={{ backgroundColor: `hsl(${hue} 70% 55% / 0.15)`, color: `hsl(${hue} 80% 62%)` }}
    >
      {name.slice(0, 2).toUpperCase()}
    </span>
  )
}

function StatusDot({ status }: { status?: string }) {
  const s = (status ?? "").toUpperCase()
  return (
    <span className="relative flex h-2.5 w-2.5 shrink-0">
      {s.includes("RUN") || s.includes("START") ? (
        <>
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-violet-400 opacity-60" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-violet-500" />
        </>
      ) : s.includes("COMPLETE") || s.includes("SUCCESS") ? (
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
      ) : s.includes("FAIL") || s.includes("ERROR") ? (
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-red-500" />
      ) : (
        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-muted-foreground/50" />
      )}
    </span>
  )
}

function ToolExecutions({ events, loading }: { events: OperationsEvent[]; loading: boolean }) {
  if (loading)
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12" />
        ))}
      </div>
    )

  const executions = events.filter((e) => e.category === "execution")
  if (!executions.length)
    return (
      <EmptyState
        title="No tool executions"
        description="Risk-gated tool calls will stream here."
        className="min-h-[180px]"
      />
    )

  return (
    <div className="space-y-1">
      {executions.slice(0, 8).map((e, i) => {
        const started = e.type === "tool_execution_started"
        const done = e.type === "tool_execution_completed"
        return (
          <div key={e.event_id ?? i} className="flex items-center gap-3 rounded-md p-2 hover:bg-muted/30">
            <span
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-md",
                done && "bg-emerald-500/10 text-emerald-500",
                started && "bg-amber-500/10 text-amber-500",
                !done && !started && "bg-muted text-muted-foreground",
              )}
            >
              {done ? <CheckCircle2 className="h-3.5 w-3.5" /> : started ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <XCircle className="h-3.5 w-3.5" />}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm capitalize">{e.action || titleCase(e.type)}</p>
              <p className="truncate text-xs text-muted-foreground">
                {e.agent ? `${e.agent} · ` : ""}
                {e.duration_ms ? formatDuration(e.duration_ms) : formatRelativeTime(e.timestamp)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}