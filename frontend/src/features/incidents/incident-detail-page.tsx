import { ArrowLeft, Bot, CheckCircle2, Loader2, Pencil, Play, Trash2, XCircle } from "lucide-react"
import { useParams, useNavigate } from "react-router-dom"
import { useState } from "react"
import { toast } from "sonner"
import { useQueryClient } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { ErrorState, EmptyState, LoadingState } from "@/components/shared/states"
import { SeverityBadge, StatusBadge } from "@/components/shared/status-badges"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { useIncident, useIncidentTimeline, incidentKeys, updateIncident, deleteIncident } from "./hooks"
import { EditIncidentDialog } from "./edit-incident-dialog"
import { cn, formatDateTime, formatRelativeTime, titleCase } from "@/lib/utils"
import type { AIResponse, Incident, WorkflowState } from "@/types/api"

export function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const incident = useIncident(id)
  const timeline = useIncidentTimeline(id)
  const [running, setRunning] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<AIResponse | null>(null)
  const [deleting, setDeleting] = useState(false)

  if (incident.isPending) return <DetailSkeleton />
  if (incident.isError || !incident.data) {
    return (
      <div className="container px-6 py-8">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <ErrorState message={incident.error?.message ?? "Incident not found"} onRetry={() => incident.refetch()} />
      </div>
    )
  }

  const inc = incident.data!

  async function runWorkflow() {
    setRunning(true)
    try {
      const state = await feClient.post<WorkflowState>(`/incidents/${inc.id}/workflow/run`, {
        title: inc.title,
        description: inc.description,
        severity: inc.severity,
      })
      toast.success(`Workflow ${titleCase(state.workflow_status)}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Workflow run failed")
    } finally {
      setRunning(false)
    }
  }

  async function analyze() {
    setAnalyzing(true)
    setAnalysis(null)
    try {
      const res = await feClient.post<AIResponse>("/incidents/analyze", {
        title: inc.title,
        description: inc.description,
        severity: inc.severity,
      })
      setAnalysis(res)
      toast.success("Analysis complete")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Analysis failed")
    } finally {
      setAnalyzing(false)
    }
  }

  async function handleEdit(values: { title: string; description: string; severity: Incident["severity"]; status: Incident["status"] }) {
    try {
      await updateIncident(inc.id, { ...values, source: inc.source })
      queryClient.invalidateQueries({ queryKey: incidentKeys.detail(inc.id) })
      queryClient.invalidateQueries({ queryKey: incidentKeys.list({}) })
      toast.success("Incident updated")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Update failed")
    }
  }

  async function handleDelete() {
    setDeleting(true)
    try {
      await deleteIncident(inc.id)
      toast.success("Incident deleted")
      navigate("/incidents")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Delete failed")
      setDeleting(false)
    }
  }

  return (
    <div className="container px-6 py-8">
      <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to incidents
      </Button>

      <PageHeader
        eyebrow="Incident"
        title={inc.title}
        description={`${inc.source} · ${inc.id}`}
        action={
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={inc.status} />
            <SeverityBadge severity={inc.severity} />
            <EditIncidentDialog incident={inc} onSubmit={handleEdit}>
              <Button variant="outline" size="sm">
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </Button>
            </EditIncidentDialog>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete this incident?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This permanently removes the incident and its timeline. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete} disabled={deleting}>
                    {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <Button onClick={runWorkflow} disabled={running}>
              {running ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Run workflow
            </Button>
          </div>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <CardShell title="Description">
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground">
              {inc.description}
            </p>
          </CardShell>

          <CardShell
            title="Timeline"
            description="Real-time incident timeline"
            action={<Badge variant="outline">Live</Badge>}
          >
            <Timeline events={timeline.data ?? []} loading={timeline.isPending} />
          </CardShell>
        </div>

        <div className="space-y-4">
          <CardShell title="Details">
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">ID</dt>
                <dd className="font-mono text-xs">{inc.id.slice(0, 8)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Source</dt>
                <dd>{inc.source}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Created</dt>
                <dd className="tabular-nums">{formatDateTime(inc.created_at)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Updated</dt>
                <dd className="tabular-nums">{formatRelativeTime(inc.updated_at)}</dd>
              </div>
            </dl>
          </CardShell>

          <CardShell title="AI analysis">
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Run the incident workflow to remediate with the autonomous agent fleet, or analyze this incident with the AI model for a quick root-cause read.
              </p>
              <Button variant="outline" size="sm" className="w-full" onClick={runWorkflow} disabled={running}>
                <Play className="mr-2 h-4 w-4" />
                Run workflow
              </Button>
              <Button size="sm" className="w-full" onClick={analyze} disabled={analyzing}>
                {analyzing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bot className="mr-2 h-4 w-4" />}
                {analyzing ? "Analyzing…" : "Analyze with AI"}
              </Button>

              {analysis && (
                <div className="space-y-3 rounded-lg border bg-muted/20 p-4">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="outline">
                      {analysis.severity} · {analysis.category}
                    </Badge>
                    <span className="text-xs tabular-nums text-muted-foreground">
                      {(analysis.confidence * 100).toFixed(0)}% conf
                    </span>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Summary</p>
                    <p className="text-sm">{analysis.summary}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Probable cause</p>
                    <p className="text-sm">{analysis.probable_cause}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Recommendation</p>
                    <p className="text-sm">{analysis.recommendation}</p>
                  </div>
                  <p className="text-[11px] text-muted-foreground">
                    {analysis.model} · {analysis.provider} · {(analysis.processing_time_ms / 1000).toFixed(1)}s
                  </p>
                </div>
              )}
            </div>
          </CardShell>
        </div>
      </div>
    </div>
  )
}

function Timeline({ events, loading }: { events: ReturnType<typeof useIncidentTimeline>["data"]; loading: boolean }) {
  if (loading) return <LoadingState label="Loading timeline…" className="min-h-[200px]" />
  if (!events?.length)
    return (
      <EmptyState
        title="No timeline events"
        description="Workflow and agent events will appear here as they run."
        className="min-h-[200px]"
      />
    )
  return (
    <div className="relative space-y-0">
      {events.map((e, i) => {
        const done = e.type.includes("completed") || e.type.includes("resolved")
        const running = e.type.includes("started")
        return (
          <div key={e.event_id ?? i} className="relative flex gap-3 pb-4 last:pb-0">
            {i < events.length - 1 && <span className="absolute left-[11px] top-6 h-full w-px bg-border" />}
            <span
              className={cn(
                "relative z-10 mt-0.5 flex h-[23px] w-[23px] shrink-0 items-center justify-center rounded-full border bg-card",
                done && "border-emerald-500/40 text-emerald-500",
                running && "border-violet-500/40 text-violet-500",
                !done && !running && "text-muted-foreground",
              )}
            >
              {done ? <CheckCircle2 className="h-3.5 w-3.5" /> : running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <XCircle className="h-3.5 w-3.5" />}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{titleCase(e.action || e.type)}</p>
                <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
                  {formatRelativeTime(e.timestamp)}
                </span>
              </div>
              <p className="truncate text-xs text-muted-foreground">
                {e.agent ? `${e.agent} · ` : ""}
                {e.status ? titleCase(e.status) : titleCase(e.type)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="container px-6 py-8">
      <Skeleton className="h-4 w-24" />
      <div className="mt-6 space-y-2">
        <Skeleton className="h-8 w-96" />
        <Skeleton className="h-4 w-48" />
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Skeleton className="h-32" />
          <Skeleton className="h-72" />
        </div>
        <Skeleton className="h-72" />
      </div>
    </div>
  )
}