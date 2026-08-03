import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Boxes, GitBranch, Play, Plus, Workflow } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { feClient } from "@/services/api"
import { cn, titleCase } from "@/lib/utils"
import type { DashboardSnapshot, Playbook, PlaybookStep } from "@/types/api"

interface CreatedPipeline {
  id: string
  name: string
  description: string
  stages: string[]
  active: boolean
}

interface AgentSummary {
  total_agents: number
  total_runs: number
  overall_success_rate: number
}

interface LifecycleRunResult {
  incident_id: string
  status: string
}

const playbookAlerts: Record<string, Record<string, unknown>> = {
  kubernetes_crash_restart: {
    source: "kubernetes",
    alert_id: "pl-run-crash",
    title: "Pod crash loop detected (pipeline run)",
    description: "payments-api pod entered CrashLoopBackOff. Restarting requires approval.",
    severity: "medium",
    service: "payments",
    tags: ["crash", "restart"],
  },
  memory_restart: {
    source: "kubernetes",
    alert_id: "pl-run-memory",
    title: "Memory pressure on worker node (pipeline run)",
    description: "worker-pool node under memory pressure; pods at risk of OOMKill.",
    severity: "high",
    service: "workers",
    tags: ["memory"],
  },
  kubernetes_health_check: {
    source: "kubernetes",
    alert_id: "pl-run-health",
    title: "Health check degraded (pipeline run)",
    description: "Health probe latency elevated on payments-api.",
    severity: "low",
    service: "payments",
    tags: ["health", "status"],
  },
}

const fallbackAlert = {
  source: "kubernetes",
  alert_id: "pl-run-generic",
  title: "New monitoring alert (pipeline run)",
  description: "Triggered via pipeline run.",
  severity: "low",
  service: "generic",
  tags: ["health"],
}

const riskStyles: Record<string, string> = {
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-600",
  high: "border-destructive/30 bg-destructive/10 text-destructive",
}

export function PipelinesPage() {
  const queryClient = useQueryClient()

  const playbooks = useQuery({
    queryKey: ["pipelines", "playbooks"],
    queryFn: () => feClient.get<Playbook[]>("/aiops/playbooks"),
  })
  const dashboard = useQuery({
    queryKey: ["pipelines", "dashboard"],
    queryFn: () => feClient.get<DashboardSnapshot>("/operations/dashboard"),
  })
  const agents = useQuery({
    queryKey: ["pipelines", "agents"],
    queryFn: () => feClient.get<AgentSummary>("/optimization/agents/summary"),
  })

  const [created, setCreated] = useState<CreatedPipeline[]>([])

  const run = useMutation({
    mutationFn: (playbook: Playbook) =>
      feClient.post<LifecycleRunResult>("/aiops/lifecycle/run", playbookAlerts[playbook.name] ?? fallbackAlert),
    onSuccess: (res, playbook) => {
      toast.success(`Pipeline "${titleCase(playbook.name.replace(/_/g, " "))}" ran → ${res.status}`, {
        description: `Incident ${res.incident_id.slice(0, 8)}`,
      })
      queryClient.invalidateQueries({ queryKey: ["pipelines", "dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["pipelines", "agents"] })
    },
    onError: (err) => toast.error(err.message),
  })

  const loading = playbooks.isPending || dashboard.isPending || agents.isPending
  const totalRuns = agents.data?.total_runs ?? dashboard.data?.ai.total_agent_runs ?? 0
  const successRate = agents.data?.overall_success_rate ?? dashboard.data?.ai.agent_success_rate ?? 0

  const activeCount = playbooks.data?.length ?? 0

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Pipelines"
        description="Real remediation playbooks compiled into automated response pipelines."
        eyebrow="Automation"
        action={<CreatePipelineDialog onCreated={(p) => setCreated((prev) => [...prev, p])} />}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Pipelines" value={playbooks.data?.length ?? 0} icon={Boxes} accent="primary" hint="playbooks" />
        <StatCard label="Active" value={activeCount} icon={GitBranch} accent="success" hint="enabled" />
        <StatCard label="Total runs" value={totalRuns} icon={Play} accent="accent" hint="agent runs" />
        <StatCard label="Success rate" value={`${successRate.toFixed(1)}%`} icon={Workflow} accent="warning" hint="overall" />
      </div>

      {loading ? (
        <div className="mt-4">
          <LoadingState label="Loading pipelines…" />
        </div>
      ) : (playbooks.data?.length ?? 0) + created.length === 0 ? (
        <div className="mt-4">
          <CardShell title="Pipelines">
            <EmptyState title="No pipelines" description="Register remediation playbooks to automate incident response." />
          </CardShell>
        </div>
      ) : (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {(playbooks.data ?? []).map((playbook) => (
            <PlaybookCard key={playbook.name} playbook={playbook} running={run.isPending} onRun={() => run.mutate(playbook)} />
          ))}
          {created.map((p) => (
            <CardShell
              key={p.id}
              title={p.name}
              description={p.description}
              action={<Badge variant={p.active ? "default" : "secondary"}>{p.active ? "Active" : "Paused"}</Badge>}
            >
              <div className="flex items-center gap-2">
                {p.stages.map((s, i) => (
                  <div key={s} className="flex items-center gap-2">
                    <span className="rounded-md border bg-muted/40 px-2.5 py-1 text-xs font-medium capitalize">{s}</span>
                    {i < p.stages.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />}
                  </div>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => toast.success(`Pipeline "${p.name}" queued`)}>
                  <Play className="mr-1.5 h-3.5 w-3.5" />
                  Run
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setCreated((prev) => prev.map((x) => (x.id === p.id ? { ...x, active: !x.active } : x)))}
                >
                  {p.active ? "Pause" : "Resume"}
                </Button>
              </div>
            </CardShell>
          ))}
        </div>
      )}
    </div>
  )
}

function PlaybookCard({
  playbook,
  running,
  onRun,
}: {
  playbook: Playbook
  running: boolean
  onRun: () => void
}) {
  return (
    <CardShell
      title={titleCase(playbook.name.replace(/_/g, " "))}
      description={playbook.description}
      action={
        <Badge variant="outline">
          v{playbook.version} · {playbook.steps.length} steps
        </Badge>
      }
    >
      <div className="flex flex-wrap items-center gap-2">
        {playbook.steps.map((step, i) => (
          <div key={step.name} className="flex items-center gap-2">
            <div className="flex items-center gap-2 rounded-lg border bg-muted/40 px-2.5 py-1.5">
              <span className="text-xs font-medium capitalize">{titleCase(step.name.replace(/_/g, " "))}</span>
              <StepToolBadge step={step} />
            </div>
            {i < playbook.steps.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />}
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <span>Registered remediation playbook</span>
        <span className="font-mono">{playbook.name}</span>
      </div>
      <div className="mt-3 flex gap-2">
        <Button size="sm" onClick={onRun} disabled={running}>
          {running ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground" /> : <Play className="mr-1.5 h-3.5 w-3.5" />}
          Run pipeline
        </Button>
        <Button size="sm" variant="ghost" onClick={() => toast.info(`Editing ${playbook.name}`)}>
          Edit
        </Button>
      </div>
    </CardShell>
  )
}

function StepToolBadge({ step }: { step: PlaybookStep }) {
  return (
    <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", riskStyles[step.risk_level] ?? "bg-muted text-muted-foreground")}>
      {step.tool}.{step.action}
    </span>
  )
}

function CreatePipelineDialog({ onCreated }: { onCreated: (p: CreatedPipeline) => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")

  function create() {
    if (!name.trim()) {
      toast.error("Pipeline name is required")
      return
    }
    onCreated({
      id: crypto.randomUUID(),
      name: name.trim(),
      description: description.trim() || "Automated response pipeline.",
      stages: ["ingest", "analyze", "execute"],
      active: true,
    })
    toast.success("Pipeline created")
    setOpen(false)
    setName("")
    setDescription("")
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New pipeline
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create pipeline</DialogTitle>
          <DialogDescription>Compose workflows into an automated pipeline.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="pl-name">Name</Label>
            <Input id="pl-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. On-call triage" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="pl-desc">Description</Label>
            <Textarea id="pl-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="What does this pipeline do?" />
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <p className="text-sm font-medium">Enable immediately</p>
              <p className="text-xs text-muted-foreground">Start running on new alerts</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={create}>Create</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
