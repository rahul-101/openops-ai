import { ArrowRight, Boxes, GitBranch, Play, Plus, Workflow } from "lucide-react"
import { useState } from "react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { EmptyState } from "@/components/shared/states"
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
import { toast } from "sonner"

interface Pipeline {
  id: string
  name: string
  description: string
  stages: string[]
  active: boolean
  runs: number
  lastRun?: string
}

const seedPipelines: Pipeline[] = [
  {
    id: "p1",
    name: "On-call triage",
    description: "Auto-triage alerts, page the right team, and open incident records.",
    stages: ["ingest", "classify", "notify"],
    active: true,
    runs: 128,
  },
  {
    id: "p2",
    name: "Auto-remediation",
    description: "Run risk-gated remediations with rollback and verification.",
    stages: ["analyze", "decide", "execute", "verify"],
    active: true,
    runs: 64,
  },
]

export function PipelinesPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>(seedPipelines)

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Pipelines"
        description="Compose workflows into automated incident response pipelines."
        eyebrow="Automation"
        action={<CreatePipelineDialog onCreated={(p) => setPipelines((prev) => [...prev, p])} />}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Pipelines" value={pipelines.length} icon={Boxes} accent="primary" hint="configured" />
        <StatCard label="Active" value={pipelines.filter((p) => p.active).length} icon={GitBranch} accent="success" hint="enabled" />
        <StatCard label="Total runs" value={pipelines.reduce((acc, p) => acc + p.runs, 0)} icon={Play} accent="accent" hint="all time" />
        <StatCard label="Avg stages" value="3" icon={Workflow} accent="warning" hint="per pipeline" />
      </div>

      {pipelines.length === 0 ? (
        <div className="mt-4">
          <CardShell title="Pipelines">
            <EmptyState title="No pipelines" description="Create your first pipeline to automate incident response." />
          </CardShell>
        </div>
      ) : (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {pipelines.map((p) => (
            <CardShell
              key={p.id}
              title={p.name}
              description={p.description}
              action={
                <Badge variant={p.active ? "default" : "secondary"}>{p.active ? "Active" : "Paused"}</Badge>
              }
            >
              <div className="flex items-center gap-2">
                {p.stages.map((s, i) => (
                  <div key={s} className="flex items-center gap-2">
                    <span className="rounded-md border bg-muted/40 px-2.5 py-1 text-xs font-medium capitalize">
                      {s}
                    </span>
                    {i < p.stages.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />}
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                <span>{p.runs} runs</span>
                <span>{p.lastRun ?? "never run"}</span>
              </div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => toast.success(`Pipeline "${p.name}" queued`)}>
                  <Play className="mr-1.5 h-3.5 w-3.5" />
                  Run
                </Button>
                <Button size="sm" variant="ghost" onClick={() => togglePipeline(p.id)}>
                  {p.active ? "Pause" : "Resume"}
                </Button>
              </div>
            </CardShell>
          ))}
        </div>
      )}
    </div>
  )

  function togglePipeline(id: string) {
    setPipelines((prev) => prev.map((p) => (p.id === id ? { ...p, active: !p.active } : p)))
  }
}

function CreatePipelineDialog({ onCreated }: { onCreated: (p: Pipeline) => void }) {
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
      runs: 0,
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