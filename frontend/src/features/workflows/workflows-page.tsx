import { useQuery } from "@tanstack/react-query"
import { Box, GitBranch, Play, Server, Workflow as WorkflowIcon } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { cn, titleCase } from "@/lib/utils"
import type { LifecycleRecord } from "@/types/api"

export const workflowKeys = {
  all: ["workflows"] as const,
  lifecycle: () => [...workflowKeys.all, "lifecycle"] as const,
  playbooks: () => [...workflowKeys.all, "playbooks"] as const,
}

export function useWorkflows() {
  return useQuery({
    queryKey: workflowKeys.lifecycle(),
    queryFn: () => feClient.get<LifecycleRecord[]>("/aiops/lifecycle"),
    refetchInterval: 15_000,
  })
}

export function WorkflowsPage() {
  const workflows = useWorkflows()
  const [expanded, setExpanded] = useState<string | null>(null)

  const workflowsData = workflows.data ?? []
  const running = workflowsData.filter((w) => w.status === "running" || w.status === "in_progress").length
  const completed = workflowsData.filter((w) => w.status === "completed").length
  const autoRunRate = workflowsData.length ? completed / workflowsData.length : 0

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Workflows"
        description="End-to-end incident response workflows and their execution stages."
        eyebrow="Automation"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Workflows" value={workflowsData.length || "—"} icon={WorkflowIcon} accent="primary" hint="records" />
        <StatCard label="Running" value={running} icon={Play} accent="accent" hint="in progress" />
        <StatCard label="Resolved" value={workflowsData.filter((w) => w.status === "resolved").length} icon={Box} accent="success" hint="completed" />
        <StatCard label="Auto-run rate" value={workflowsData.length ? `${(autoRunRate * 100).toFixed(0)}%` : "—"} icon={GitBranch} accent="warning" hint="detected → action" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <CardShell title="Workflow runs" description="Latest incident lifecycle executions" className="lg:col-span-2">
          <WorkflowList workflows={workflowsData} loading={workflows.isPending} expanded={expanded} onToggle={setExpanded} />
        </CardShell>
        <CardShell title="Workflow stages" description="The five-stage incident lifecycle">
          <StagesList />
        </CardShell>
      </div>
    </div>
  )
}

function WorkflowList({
  workflows,
  loading,
  expanded,
  onToggle,
}: {
  workflows: LifecycleRecord[]
  loading: boolean
  expanded: string | null
  onToggle: (id: string | null) => void
}) {
  if (loading) return <LoadingState label="Loading workflows…" className="min-h-[300px]" />
  if (!workflows.length)
    return (
      <EmptyState
        title="No workflows yet"
        description="Run the incident lifecycle from the Operations page to see workflow executions."
        className="min-h-[300px]"
      />
    )

  return (
    <div className="space-y-2">
      {workflows.map((wf) => {
        const isExpanded = expanded === wf.incident_id
        const isRunning = wf.status === "running" || wf.status === "in_progress"
        return (
          <div key={wf.incident_id} className="rounded-lg border transition-colors hover:bg-muted/20">
            <button
              className="flex w-full items-center gap-3 p-3 text-left"
              onClick={() => onToggle(isExpanded ? null : wf.incident_id)}
              aria-expanded={isExpanded}
            >
              <span className={cn("flex h-8 w-8 items-center justify-center rounded-md", isRunning ? "bg-violet-500/10 text-violet-500" : "bg-emerald-500/10 text-emerald-500")}>
                {isRunning ? <Play className="h-4 w-4 animate-pulse" /> : <Box className="h-4 w-4" />}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">inc {wf.incident_id.slice(0, 8)}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {(wf.steps ?? []).length} stages · servicenow {wf.servicenow_updated ? "updated" : "pending"} · learning {wf.learning_recorded ? "recorded" : "pending"}
                </p>
              </div>
              <Badge variant={isRunning ? "secondary" : "outline"}>{titleCase(wf.status)}</Badge>
            </button>
            {isExpanded && (
              <div className="border-t px-3 py-3">
                <div className="space-y-1.5">
                  {(wf.steps ?? []).map((step, i) => (
                    <div key={i} className="flex items-center gap-3 text-xs">
                      <StepIcon status={step.status} />
                      <span className="w-24 shrink-0 font-medium capitalize">{step.stage}</span>
                      <span className="flex-1 truncate text-muted-foreground">{step.details}</span>
                      <Badge variant="outline" className="shrink-0">
                        {titleCase(step.status)}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function StepIcon({ status }: { status: string }) {
  const s = status.toUpperCase()
  return (
    <span
      className={cn(
        "h-2 w-2 shrink-0 rounded-full",
        s === "COMPLETED" && "bg-emerald-500",
        s === "RUNNING" && "animate-pulse bg-violet-500",
        (s === "FAILED" || s === "BLOCKED") && "bg-red-500",
        !["COMPLETED", "RUNNING", "FAILED", "BLOCKED"].includes(s) && "bg-muted-foreground/40",
      )}
    />
  )
}

const stages = [
  { name: "Ingest", desc: "Normalize alerts from all sources", color: "text-sky-500" },
  { name: "Analyze", desc: "Multi-agent reasoning & RCA", color: "text-violet-500" },
  { name: "Decide", desc: "Confidence + risk-gated decisions", color: "text-fuchsia-500" },
  { name: "Execute", desc: "Approved remediations run", color: "text-amber-500" },
  { name: "Verify", desc: "Self-verification of recovery", color: "text-emerald-500" },
]

function StagesList() {
  return (
    <div className="space-y-0">
      {stages.map((stage, i) => (
        <div key={stage.name} className="relative flex gap-3 pb-5 last:pb-0">
          {i < stages.length - 1 && <span className="absolute left-[11px] top-6 h-full w-px bg-border" />}
          <span className={cn("relative z-10 mt-0.5 h-[23px] w-[23px] shrink-0 rounded-full border bg-card", stage.color)}>
            <Server className="h-3 w-3" />
          </span>
          <div>
            <p className="text-sm font-medium">{stage.name}</p>
            <p className="text-xs text-muted-foreground">{stage.desc}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export function setupHint() {
  toast.info("Pipelines compose multiple workflows. Configure triggers and steps.")
}