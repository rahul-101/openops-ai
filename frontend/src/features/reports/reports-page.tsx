import { useQuery } from "@tanstack/react-query"
import { Calendar, Download, FileText, Sparkles } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
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
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { feClient } from "@/services/api"
import { formatDateTime, titleCase } from "@/lib/utils"
import type { Approval, DashboardSnapshot, LifecycleRecord, ModelStats } from "@/types/api"

type ReportKind = "weekly" | "incidents" | "cost" | "audit"

interface ReportSection {
  heading: string
  lines: string[]
}

interface Report {
  id: string
  kind: ReportKind
  title: string
  generatedAt: string
  sections: ReportSection[]
  markdown: string
}

interface AgentSummary {
  total_agents: number
  total_runs: number
  overall_success_rate: number
}

const kindLabels: Record<ReportKind, string> = {
  weekly: "Weekly digest",
  incidents: "Incident report",
  cost: "Cost report",
  audit: "Audit summary",
}

function downloadMarkdown(report: Report) {
  const blob = new Blob([report.markdown], { type: "text/markdown;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `${report.title.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

export function ReportsPage() {
  const dashboard = useQuery({
    queryKey: ["reports", "dashboard"],
    queryFn: () => feClient.get<DashboardSnapshot>("/operations/dashboard"),
  })
  const lifecycle = useQuery({
    queryKey: ["reports", "lifecycle"],
    queryFn: () => feClient.get<LifecycleRecord[]>("/aiops/lifecycle"),
  })
  const approvals = useQuery({
    queryKey: ["reports", "approvals"],
    queryFn: () => feClient.get<Approval[]>("/approvals/history"),
  })
  const modelStats = useQuery({
    queryKey: ["reports", "models"],
    queryFn: () => feClient.get<ModelStats>("/governance/models/stats"),
  })
  const agents = useQuery({
    queryKey: ["reports", "agents"],
    queryFn: () => feClient.get<AgentSummary>("/optimization/agents/summary"),
  })

  const [reports, setReports] = useState<Report[]>([])
  const seeded = useRef(false)

  const loading =
    dashboard.isPending || lifecycle.isPending || approvals.isPending || modelStats.isPending || agents.isPending

  useEffect(() => {
    if (seeded.current || loading) return
    if (!dashboard.data || !lifecycle.data || !approvals.data || !modelStats.data || !agents.data) return
    seeded.current = true
    setReports((prev) => [buildReport("weekly", dashboard.data, lifecycle.data, approvals.data, modelStats.data, agents.data), ...prev])
  }, [loading, dashboard.data, lifecycle.data, approvals.data, modelStats.data, agents.data])

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Reports"
        description="Operational summaries composed from live pipeline data."
        eyebrow="Intelligence"
        action={
          <GenerateReportDialog
            disabled={loading}
            onGenerated={(kind) =>
              setReports((prev) => [
                buildReport(kind, dashboard.data!, lifecycle.data!, approvals.data!, modelStats.data!, agents.data!),
                ...prev,
              ])
            }
          />
        }
      />

      {loading ? (
        <LoadingState label="Aggregating live pipeline data…" />
      ) : reports.length === 0 ? (
        <CardShell title="Reports">
          <EmptyState title="No reports yet" description="Generate your first operational report from live data." />
        </CardShell>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {reports.map((r) => (
            <CardShell key={r.id} title={r.title} action={<Badge variant="outline">Markdown</Badge>}>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                <span>{kindLabels[r.kind]}</span>
                <span>·</span>
                <span>{formatDateTime(r.generatedAt)}</span>
              </div>
              <div className="mt-3 space-y-3">
                {r.sections.map((section) => (
                  <div key={section.heading}>
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{section.heading}</p>
                    <ul className="mt-1 space-y-0.5 text-sm text-foreground/90">
                      {section.lines.map((line, i) => (
                        <li key={i}>{line}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => downloadMarkdown(r)}>
                  <Download className="mr-1.5 h-3.5 w-3.5" />
                  Download .md
                </Button>
                <Button size="sm" variant="ghost" onClick={() => toast.info("Opening report…")}>
                  <FileText className="mr-1.5 h-3.5 w-3.5" />
                  View
                </Button>
              </div>
            </CardShell>
          ))}
        </div>
      )}
    </div>
  )
}

function buildReport(
  kind: ReportKind,
  dashboard: DashboardSnapshot,
  lifecycle: LifecycleRecord[],
  approvals: Approval[],
  modelStats: ModelStats,
  agents: AgentSummary,
): Report {
  const generatedAt = new Date().toISOString()

  switch (kind) {
    case "incidents":
      return {
        id: crypto.randomUUID(),
        kind,
        title: "Incident lifecycle report",
        generatedAt,
        ...incidentSections(dashboard, lifecycle, approvals),
      }
    case "cost":
      return {
        id: crypto.randomUUID(),
        kind,
        title: "Model usage & cost report",
        generatedAt,
        ...costSections(modelStats),
      }
    case "audit":
      return {
        id: crypto.randomUUID(),
        kind,
        title: "Autonomous response audit",
        generatedAt,
        ...auditSections(dashboard, lifecycle, approvals, agents),
      }
    default:
      return {
        id: crypto.randomUUID(),
        kind: "weekly",
        title: "Weekly autonomous response summary",
        generatedAt,
        ...weeklySections(dashboard, approvals, modelStats, agents),
      }
  }
}

function weeklySections(
  dashboard: DashboardSnapshot,
  approvals: Approval[],
  modelStats: ModelStats,
  agents: AgentSummary,
) {
  const i = dashboard.incidents
  const a = dashboard.ai
  return {
    sections: [
      {
        heading: "Incidents",
        lines: [
          `Total incidents: ${i.total_incidents}`,
          `Resolved: ${i.resolved_incidents} · Open: ${i.open_incidents}`,
          `Auto-resolution rate: ${i.auto_resolution_rate}%`,
          `Average resolution time: ${i.average_resolution_time_s.toFixed(2)}s`,
        ],
      },
      {
        heading: "Autonomous AI",
        lines: [
          `Agents active: ${agents.total_agents} · Runs: ${agents.total_runs}`,
          `Agent success rate: ${agents.overall_success_rate.toFixed(1)}%`,
          `Tokens consumed: ${a.input_tokens + a.output_tokens}`,
          `Model spend: $${a.cost_usd.toFixed(4)}`,
        ],
      },
      {
        heading: "Approvals",
        lines: approvalLines(approvals),
      },
    ],
    markdown: `# Weekly Autonomous Response Summary\n\nGenerated ${formatDateTime(generatedTimestamp())}\n\n## Incidents\n- Total incidents: ${i.total_incidents}\n- Resolved: ${i.resolved_incidents} · Open: ${i.open_incidents}\n- Auto-resolution rate: ${i.auto_resolution_rate}%\n- Average resolution time: ${i.average_resolution_time_s.toFixed(2)}s\n\n## Autonomous AI\n- Agents active: ${agents.total_agents} · Runs: ${agents.total_runs}\n- Agent success rate: ${agents.overall_success_rate.toFixed(1)}%\n- Tokens consumed: ${a.input_tokens + a.output_tokens}\n- Model spend: $${a.cost_usd.toFixed(4)}\n\n## Approvals\n${approvalLines(approvals)
  .map((l) => `- ${l}`)
  .join("\n")}\n\n## Model usage\n${Object.entries(modelStats.providers)
  .map(([name, p]) => `- ${name}: ${p.requests} requests · ${p.tokens} tokens · $${p.cost_usd.toFixed(4)}`)
  .join("\n")}\n`,
  }
}

function incidentSections(dashboard: DashboardSnapshot, lifecycle: LifecycleRecord[], approvals: Approval[]) {
  const i = dashboard.incidents
  return {
    sections: [
      {
        heading: "Pipeline throughput",
        lines: [
          `Lifecycle records: ${lifecycle.length}`,
          `Completed: ${lifecycle.filter((l) => l.status === "completed").length}`,
          `Open incidents: ${i.open_incidents}`,
        ],
      },
      {
        heading: "Lifecycle records",
        lines: lifecycle
          .slice(-8)
          .map((l) => `${l.incident_id.slice(0, 8)} — ${titleCase(l.status)}${l.servicenow_updated ? " · ServiceNow updated" : ""}`),
      },
      {
        heading: "Approvals",
        lines: approvalLines(approvals),
      },
    ],
    markdown: `# Incident Report\n\n## Pipeline throughput\n- Lifecycle records: ${lifecycle.length}\n- Completed: ${lifecycle.filter((l) => l.status === "completed").length}\n\n## Lifecycle records\n${lifecycle
      .slice(-8)
      .map((l) => `- ${l.incident_id} — ${titleCase(l.status)}`)
      .join("\n")}\n\n## Approvals\n${approvalLines(approvals)
      .map((l) => `- ${l}`)
      .join("\n")}\n`,
  }
}

function costSections(modelStats: ModelStats) {
  return {
    sections: [
      {
        heading: "Summary",
        lines: [
          `Total requests: ${modelStats.total_requests}`,
          `Total tokens: ${modelStats.total_tokens}`,
          `Total cost: $${modelStats.total_cost_usd.toFixed(4)}`,
          `Average latency: ${modelStats.average_latency_ms.toFixed(0)}ms`,
        ],
      },
      {
        heading: "Per provider",
        lines: Object.entries(modelStats.providers).map(
          ([name, p]) => `${name} — ${p.requests} requests · ${p.tokens} tokens · $${p.cost_usd.toFixed(4)}`,
        ),
      },
    ],
    markdown: `# Model Usage & Cost Report\n\n- Total requests: ${modelStats.total_requests}\n- Total tokens: ${modelStats.total_tokens}\n- Total cost: $${modelStats.total_cost_usd.toFixed(4)}\n- Average latency: ${modelStats.average_latency_ms.toFixed(0)}ms\n\n## Per provider\n${Object.entries(modelStats.providers)
      .map(([name, p]) => `- ${name}: ${p.requests} requests · ${p.tokens} tokens · $${p.cost_usd.toFixed(4)}`)
      .join("\n")}\n`,
  }
}

function auditSections(
  dashboard: DashboardSnapshot,
  lifecycle: LifecycleRecord[],
  approvals: Approval[],
  agents: AgentSummary,
) {
  return {
    sections: [
      {
        heading: "Agent performance",
        lines: [
          `Runs: ${agents.total_runs} · Success rate: ${agents.overall_success_rate.toFixed(1)}%`,
          `Successful actions: ${dashboard.execution.successful_actions} · Failed: ${dashboard.execution.failed_actions} · Rollbacks: ${dashboard.execution.rollback_count}`,
        ],
      },
      {
        heading: "Lifecycle",
        lines: [
          `Records: ${lifecycle.length} (${lifecycle.filter((l) => l.status === "completed").length} completed)`,
          `Open incidents: ${dashboard.incidents.open_incidents}`,
        ],
      },
      {
        heading: "Approvals",
        lines: approvalLines(approvals),
      },
    ],
    markdown: `# Autonomous Response Audit\n\n## Agent performance\n- Runs: ${agents.total_runs} · Success rate: ${agents.overall_success_rate.toFixed(1)}%\n- Successful actions: ${dashboard.execution.successful_actions} · Failed: ${dashboard.execution.failed_actions} · Rollbacks: ${dashboard.execution.rollback_count}\n\n## Lifecycle\n- Records: ${lifecycle.length} (${lifecycle.filter((l) => l.status === "completed").length} completed)\n- Open incidents: ${dashboard.incidents.open_incidents}\n\n## Approvals\n${approvalLines(approvals)
      .map((l) => `- ${l}`)
      .join("\n")}\n`,
  }
}

function approvalLines(approvals: Approval[]) {
  const pending = approvals.filter((a) => a.status === "pending").length
  const approved = approvals.filter((a) => a.status === "approved").length
  const executed = approvals.filter((a) => a.status === "executed").length
  const rejected = approvals.filter((a) => a.status === "rejected").length
  return [
    `Total requests: ${approvals.length}`,
    `Pending: ${pending} · Approved: ${approved} · Executed: ${executed} · Rejected: ${rejected}`,
  ]
}

function generatedTimestamp() {
  return new Date().toISOString()
}

function GenerateReportDialog({
  disabled,
  onGenerated,
}: {
  disabled: boolean
  onGenerated: (kind: ReportKind) => void
}) {
  const [open, setOpen] = useState(false)
  const [kind, setKind] = useState<ReportKind>("weekly")

  function generate() {
    onGenerated(kind)
    toast.success("Report generated from live data")
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button disabled={disabled}>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate report
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate report</DialogTitle>
          <DialogDescription>Compose a report from live pipeline metrics, lifecycle and approval data.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="report-kind">Report type</Label>
            <Select value={kind} onValueChange={(v) => setKind(v as ReportKind)}>
              <SelectTrigger id="report-kind">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weekly">Weekly digest</SelectItem>
                <SelectItem value="incidents">Incident report</SelectItem>
                <SelectItem value="cost">Cost report</SelectItem>
                <SelectItem value="audit">Audit summary</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={generate}>Generate</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
