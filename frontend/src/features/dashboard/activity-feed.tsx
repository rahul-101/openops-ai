import { Bot, CheckCircle2 } from "lucide-react"
import { useState } from "react"

import { useSse } from "@/hooks/use-sse"
import { useOperationsEvents } from "./hooks"
import { EmptyState } from "@/components/shared/states"
import { Skeleton } from "@/components/ui/skeleton"
import { cn, formatRelativeTime, titleCase } from "@/lib/utils"
import type { OperationsEvent } from "@/types/api"

const typeIcon: Record<string, typeof Bot> = {
  analysis_started: Bot,
  rca_completed: Bot,
  decision_created: Bot,
  tool_execution_started: Bot,
  tool_execution_completed: CheckCircle2,
  incident_created: Bot,
  incident_resolved: CheckCircle2,
}

const typeColor: Record<string, string> = {
  incident_created: "text-sky-500",
  analysis_started: "text-violet-500",
  rca_completed: "text-violet-500",
  decision_created: "text-fuchsia-500",
  tool_execution_started: "text-amber-500",
  tool_execution_completed: "text-emerald-500",
  incident_resolved: "text-emerald-500",
}

export function ActivityFeed({ limit = 12 }: { limit?: number }) {
  const [live, setLive] = useState<OperationsEvent[]>([])
  const events = useOperationsEvents(limit)
  const { connected } = useSse(import.meta.env.VITE_SSE_URL ?? "/api/operations/events/stream", {
    onEvent: (ev) => {
      const e = ev as OperationsEvent
      if (e && e.event_id) {
        setLive((prev) => [e, ...prev].slice(0, limit))
      }
    },
  })

  const combined = [...live, ...(events.data ?? [])]

  return (
    <div>
      <div className="mb-2 flex items-center gap-2 text-xs">
        <span
          className={cn(
            "inline-flex h-2 w-2 rounded-full",
            connected ? "bg-emerald-500" : "bg-amber-500",
          )}
        />
        <span className="text-muted-foreground">{connected ? "Live" : "Snapshot"}</span>
      </div>
      {events.isPending && !combined.length ? (
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-12" />
          ))}
        </div>
      ) : combined.length === 0 ? (
        <EmptyState title="No activity yet" description="Agent events will stream here in real time." className="min-h-[200px]" />
      ) : (
        <ul className="space-y-1">
          {combined.slice(0, limit).map((e, i) => {
            const Icon = typeIcon[e.type] ?? Bot
            return (
              <li key={e.event_id ?? i} className="flex items-start gap-3 rounded-md px-2 py-1.5 hover:bg-muted/40">
                <span className={cn("mt-0.5", typeColor[e.type] ?? "text-muted-foreground")}>
                  <Icon className="h-4 w-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm">{titleCase(e.action || e.type || "Event")}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {e.agent ? `${e.agent} · ` : ""}
                    {e.incident_id ? `inc ${e.incident_id.slice(0, 8)} · ` : ""}
                    {formatRelativeTime(e.timestamp)}
                  </p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}