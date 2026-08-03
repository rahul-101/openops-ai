import { Search } from "lucide-react"
import { useMemo, useState } from "react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { EmptyState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { cn, formatDateTime } from "@/lib/utils"
import { useOperationsEvents } from "@/features/operations/hooks"

const levelStyles: Record<string, string> = {
  info: "text-sky-500",
  success: "text-emerald-500",
  warn: "text-amber-500",
  error: "text-red-500",
}

export function LogsPage() {
  const events = useOperationsEvents(200)
  const [query, setQuery] = useState("")
  const [level, setLevel] = useState("all")

  const rows = useMemo(() => {
    const source = events.data ?? []
    return source
      .filter((e) => {
        if (level !== "all" && e.category !== level) return false
        if (!query.trim()) return true
        const q = query.toLowerCase()
        return [e.type, e.action, e.agent, e.incident_id, e.status].some((v) =>
          (v ?? "").toLowerCase().includes(q),
        )
      })
      .slice(0, 300)
  }, [events.data, query, level])

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Logs"
        description="Streaming operational event logs across the platform."
        eyebrow="Intelligence"
        action={<Badge variant="outline" className="gap-1.5"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />Live</Badge>}
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter logs…" className="pl-9 font-mono" />
        </div>
        <Select value={level} onValueChange={setLevel}>
          <SelectTrigger className="w-full sm:w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            <SelectItem value="incident">Incident</SelectItem>
            <SelectItem value="agent">Agent</SelectItem>
            <SelectItem value="execution">Execution</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <CardShell title="Event log" description="All normalized operations events">
        {events.isPending ? (
          <div className="space-y-2">
            {Array.from({ length: 20 }).map((_, i) => (
              <Skeleton key={i} className="h-9" />
            ))}
          </div>
        ) : rows.length === 0 ? (
          <EmptyState title="No log entries" description="Events stream here as the platform operates." className="min-h-[300px]" />
        ) : (
          <div className="scrollbar-none overflow-x-auto">
            <div className="min-w-[720px] space-y-0.5 font-mono text-[13px] leading-relaxed">
              {rows.map((e, i) => (
                <div key={e.event_id ?? i} className="flex items-start gap-3 rounded px-2 py-1 hover:bg-muted/30">
                  <span className="shrink-0 tabular-nums text-muted-foreground/70">{formatDateTime(e.timestamp)}</span>
                  <span className={cn("w-20 shrink-0", levelStyles[logLevel(e)])}>{logLevel(e)}</span>
                  <span className="w-24 shrink-0 truncate text-violet-400">[{e.category}]</span>
                  <span className="truncate">
                    <span className="text-muted-foreground">{e.agent ? `${e.agent} · ` : ""}</span>
                    {e.action || e.type}
                    {e.status ? ` → ${e.status}` : ""}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardShell>
    </div>
  )
}

function logLevel(e: { type: string; status?: string }): string {
  if (e.type.includes("completed") || e.type.includes("resolved")) return "success"
  if (e.type.includes("started")) return "info"
  if (e.status?.toLowerCase().includes("fail") || e.status?.toLowerCase().includes("error")) return "error"
  if (e.status?.toLowerCase().includes("block")) return "warn"
  return "info"
}