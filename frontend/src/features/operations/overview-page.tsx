import {
  Bot,
  CheckCircle2,
  GitBranch,
  Loader2,
  XCircle,
} from "lucide-react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useOperationsEvents, usePlaybooks } from "./hooks"
import { cn, formatRelativeTime, titleCase } from "@/lib/utils"
import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { runLifecycle, ingestAlert } from "./hooks"
import { HeroScrollDemo } from "./hero-scroll-demo"
import { toast } from "sonner"

export function OverviewPage() {
  const events = useOperationsEvents(50)
  const playbooks = usePlaybooks()

  return (
    <div className="mx-auto w-full max-w-[1440px] px-6 py-8">
      <HeroScrollDemo />

      <div className="mt-8">
        <PageHeader
        title="Operation Overview"
        description="Live telemetry of incidents, agents and remediation across the platform."
        eyebrow="Operations"
        action={
          <div className="flex items-center gap-2">
            <IngestAlertDialog />
            <RunLifecycleDialog />
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Recent events" value={events.data?.length ?? "—"} icon={GitBranch} accent="primary" hint="last snapshot" />
        <StatCard label="Playbooks" value={playbooks.data?.length ?? "—"} icon={Bot} accent="accent" hint="registered" />
        <StatCard label="Successful ops" value="—" icon={CheckCircle2} accent="success" hint="remediation actions" />
        <StatCard label="Failed ops" value="—" icon={XCircle} accent="destructive" hint="remediation actions" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <CardShell title="Event stream" description="Normalized events from all sources" className="lg:col-span-2">
          <EventStream events={events.data} loading={events.isPending} />
        </CardShell>

        <CardShell title="Playbooks" description="Registered remediation playbooks">
          <PlaybookList playbooks={playbooks.data} loading={playbooks.isPending} />
        </CardShell>
      </div>
      </div>
    </div>
  )
}

function EventStream({ events, loading }: { events: ReturnType<typeof useOperationsEvents>["data"]; loading: boolean }) {
  if (loading) return <LoadingState label="Loading events…" className="min-h-[300px]" />
  if (!events?.length)
    return (
      <EmptyState
        title="No events"
        description="Events from ingestion engines will appear here as they arrive."
        className="min-h-[300px]"
      />
    )
  return (
    <div className="relative max-h-[520px] space-y-1 overflow-y-auto pr-1">
      {events.map((e, i) => (
        <div
          key={e.event_id ?? i}
          className="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/30"
        >
          <EventIcon type={e.type} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2">
              <p className="truncate text-sm font-medium">{titleCase(e.action || e.type)}</p>
              <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                {formatRelativeTime(e.timestamp)}
              </span>
            </div>
            <p className="mt-0.5 truncate text-xs text-muted-foreground">
              {e.agent && `${e.agent} · `}
              {e.incident_id && `inc ${e.incident_id.slice(0, 8)}`}
              {e.status && ` · ${titleCase(e.status)}`}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

function EventIcon({ type }: { type: string }) {
  const styles: Record<string, string> = {
    incident_created: "bg-sky-500/10 text-sky-500",
    analysis_started: "bg-violet-500/10 text-violet-500",
    rca_completed: "bg-violet-500/10 text-violet-500",
    decision_created: "bg-fuchsia-500/10 text-fuchsia-500",
    tool_execution_started: "bg-amber-500/10 text-amber-500",
    tool_execution_completed: "bg-emerald-500/10 text-emerald-500",
    incident_resolved: "bg-emerald-500/10 text-emerald-500",
  }
  const Icon =
    type === "tool_execution_completed" || type === "incident_resolved" ? CheckCircle2 : Bot
  return (
    <span className={cn("mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md", styles[type] ?? "bg-muted text-muted-foreground")}>
      <Icon className="h-4 w-4" />
    </span>
  )
}

function PlaybookList({ playbooks, loading }: { playbooks: ReturnType<typeof usePlaybooks>["data"]; loading: boolean }) {
  if (loading) return <LoadingState label="Loading playbooks…" className="min-h-[200px]" />
  if (!playbooks?.length)
    return (
      <EmptyState title="No playbooks" description="Remediation playbooks will be listed here." className="min-h-[200px]" />
    )
  return (
    <div className="space-y-2">
      {playbooks.map((p) => (
        <div key={p.name} className="rounded-lg border p-3">
          <div className="flex items-center justify-between gap-2">
            <p className="truncate text-sm font-medium">{p.name}</p>
            <Badge variant="outline">v{p.version}</Badge>
          </div>
          <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{p.description}</p>
          <p className="mt-2 text-xs text-muted-foreground">{p.steps.length} steps</p>
        </div>
      ))}
    </div>
  )
}

const severityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

function IngestAlertDialog() {
  const [open, setOpen] = useState(false)
  const [source, setSource] = useState("prometheus")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [severity, setSeverity] = useState("MEDIUM")
  const [service, setService] = useState("api-gateway")
  const [busy, setBusy] = useState(false)

  async function submit() {
    if (!title.trim() || !description.trim()) {
      toast.error("Title and description are required")
      return
    }
    setBusy(true)
    try {
      await ingestAlert({
        source,
        title: title.trim(),
        description: description.trim(),
        severity,
        service,
        tags: ["ui"],
      })
      toast.success("Alert ingested")
      setOpen(false)
      setTitle("")
      setDescription("")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to ingest alert")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Loader2 className="mr-2 h-4 w-4" />
          Ingest alert
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ingest a raw alert</DialogTitle>
          <DialogDescription>Simulate an alert arriving from a monitoring system.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="oa-source">Source</Label>
              <Input id="oa-source" value={source} onChange={(e) => setSource(e.target.value)} placeholder="prometheus" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="oa-service">Service</Label>
              <Input id="oa-service" value={service} onChange={(e) => setService(e.target.value)} placeholder="api-gateway" />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="oa-severity">Severity</Label>
            <Select value={severity} onValueChange={setSeverity}>
              <SelectTrigger id="oa-severity">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {severityOptions.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="oa-title">Title</Label>
            <Input id="oa-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="High latency on payments API" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="oa-desc">Description</Label>
            <Textarea id="oa-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="Describe the alert…" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy}>
            {busy ? "Ingesting…" : "Ingest"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function RunLifecycleDialog() {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [severity, setSeverity] = useState("MEDIUM")
  const [busy, setBusy] = useState(false)

  async function submit() {
    if (!title.trim() || !description.trim()) {
      toast.error("Title and description are required")
      return
    }
    setBusy(true)
    try {
      const result = await runLifecycle({
        source: "ui",
        alert_id: crypto.randomUUID(),
        title: title.trim(),
        description: description.trim(),
        severity,
        service: "unknown",
        tags: ["ui-triggered"],
      })
      toast.success(`Lifecycle finished: ${result.status}`)
      setOpen(false)
      setTitle("")
      setDescription("")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Lifecycle run failed")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <GitBranch className="mr-2 h-4 w-4" />
          Run lifecycle
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Run incident lifecycle</DialogTitle>
          <DialogDescription>Kick off the full detect → analyze → decide → execute → verify loop.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="lc-severity">Severity</Label>
            <Select value={severity} onValueChange={setSeverity}>
              <SelectTrigger id="lc-severity">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {severityOptions.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lc-title">Title</Label>
            <Input id="lc-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="CPU saturation on worker pool" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="lc-desc">Description</Label>
            <Textarea id="lc-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="Describe the incident…" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy}>
            {busy ? "Running…" : "Run lifecycle"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}