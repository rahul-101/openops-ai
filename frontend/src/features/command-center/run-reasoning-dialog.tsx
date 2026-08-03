import { BrainCircuit, CheckCircle2, Loader2, Play, XCircle } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { cn } from "@/lib/utils"
import type { ReasoningReport } from "@/types/api"
import { runReason, useIngestedEvents } from "./hooks"

export function RunReasoningDialog({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const events = useIngestedEvents()
  const [selected, setSelected] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [report, setReport] = useState<ReasoningReport | null>(null)

  function close() {
    setOpen(false)
    setSelected(null)
    setReport(null)
  }

  async function run() {
    if (!selected) return
    setBusy(true)
    setReport(null)
    try {
      const result = await runReason(selected)
      setReport(result)
      toast.success("Reasoning complete")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Reasoning run failed")
    } finally {
      setBusy(false)
    }
  }

  const items = events.data ?? []

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-h-[80vh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Run reasoning</DialogTitle>
          <DialogDescription>
            Pick a normalized event and run the multi-agent reasoning pipeline over it.
          </DialogDescription>
        </DialogHeader>

        {report ? (
          <ReasoningReportView report={report} />
        ) : (
          <div className="space-y-3 py-1">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Event</p>
            {events.isPending ? (
              <div className="space-y-2">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-11" />
                ))}
              </div>
            ) : items.length === 0 ? (
              <div className="rounded-lg border border-dashed p-4 text-center text-sm text-muted-foreground">
                No ingested events yet. Ingest an alert from the Operations page first.
              </div>
            ) : (
              <div className="max-h-[320px] space-y-1 overflow-y-auto pr-1">
                {items.map((e) => (
                  <button
                    key={e.event_id}
                    onClick={() => setSelected(e.event_id)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-muted/30",
                      selected === e.event_id && "border-primary/50 bg-primary/5",
                    )}
                  >
                    <span
                      className={cn(
                        "flex h-8 w-8 shrink-0 items-center justify-center rounded-md",
                        selected === e.event_id ? "bg-primary/10 text-primary" : "bg-violet-500/10 text-violet-500",
                      )}
                    >
                      <BrainCircuit className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{e.title}</p>
                      <p className="truncate text-xs text-muted-foreground">
                        {e.source} · {e.event_id.slice(0, 8)}
                      </p>
                    </div>
                    <Badge variant="outline" className="shrink-0">
                      {e.severity}
                    </Badge>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        <DialogFooter className="gap-2">
          {report && (
            <Button variant="outline" onClick={() => setReport(null)}>
              Run another
            </Button>
          )}
          <Button variant="outline" onClick={close}>
            Close
          </Button>
          {!report && (
            <Button onClick={run} disabled={busy || !selected || items.length === 0}>
              {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              {busy ? "Reasoning…" : "Run reasoning"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function ReasoningReportView({ report }: { report: ReasoningReport }) {
  const verified = report.validated
  return (
    <div className="space-y-4 py-1">
      <div className="rounded-lg border p-4">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-medium">Incident {report.incident_id.slice(0, 8)}</p>
          <Badge variant={verified ? "outline" : "secondary"}>
            {verified ? <CheckCircle2 className="mr-1 h-3 w-3" /> : <XCircle className="mr-1 h-3 w-3" />}
            {verified ? "Validated" : "Not validated"}
          </Badge>
        </div>
        <dl className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          <div>
            <dt className="text-xs text-muted-foreground">Decision</dt>
            <dd className="mt-0.5 font-medium">{report.decision || "—"}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Confidence</dt>
            <dd className="mt-0.5 font-medium tabular-nums">{(report.confidence * 100).toFixed(0)}%</dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Risk</dt>
            <dd className="mt-0.5 font-medium capitalize">{report.risk}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted-foreground">Model</dt>
            <dd className="mt-0.5 font-medium">{String(report.model_selection?.model ?? "rule-based")}</dd>
          </div>
        </dl>
      </div>

      {(report.reasoning?.length ?? 0) > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground">Reasoning chain</p>
          <ul className="space-y-1.5">
            {report.reasoning.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-500" />
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {(report.evidence?.length ?? 0) > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground">Evidence</p>
            <ul className="space-y-1">
              {report.evidence.map((item, i) => (
                <li key={i} className="text-sm text-muted-foreground">
                  · {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {(report.alternatives?.length ?? 0) > 0 && (
          <div>
            <p className="mb-1.5 text-xs font-medium uppercase tracking-wider text-muted-foreground">Alternatives</p>
            <ul className="space-y-1">
              {report.alternatives.map((item, i) => (
                <li key={i} className="text-sm text-muted-foreground">
                  · {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {(report.agents_involved?.length ?? 0) > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {report.agents_involved.map((agent) => (
            <Badge key={agent} variant="secondary">
              {agent}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}
