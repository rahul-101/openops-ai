import { FileText, Download, Calendar, Sparkles } from "lucide-react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
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
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { useState } from "react"

interface Report {
  id: string
  title: string
  type: string
  status: "ready" | "generating"
  generatedAt: string
  format: string
}

const seedReports: Report[] = [
  {
    id: "r1",
    title: "Weekly autonomous response summary",
    type: "Weekly digest",
    status: "ready",
    generatedAt: "2h ago",
    format: "PDF",
  },
  {
    id: "r2",
    title: "Incident postmortem — payments-api latency",
    type: "Incident report",
    status: "ready",
    generatedAt: "1d ago",
    format: "Markdown",
  },
  {
    id: "r3",
    title: "Model cost optimization review",
    type: "Cost report",
    status: "ready",
    generatedAt: "3d ago",
    format: "PDF",
  },
]

export function ReportsPage() {
  const [reports, setReports] = useState<Report[]>(seedReports)

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Reports"
        description="Generated reports, postmortems and operational summaries."
        eyebrow="Intelligence"
        action={<GenerateReportDialog onGenerated={(r) => setReports((prev) => [r, ...prev])} />}
      />

      {reports.length === 0 ? (
        <CardShell title="Reports">
          <EmptyState title="No reports yet" description="Generate your first operational report." />
        </CardShell>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {reports.map((r) => (
            <CardShell key={r.id} title={r.title} action={<Badge variant="outline">{r.format}</Badge>}>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Calendar className="h-3.5 w-3.5" />
                <span>{r.type}</span>
                <span>·</span>
                <span>{r.generatedAt}</span>
              </div>
              <div className="mt-4 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => toast.success("Report downloaded")}>
                  <Download className="mr-1.5 h-3.5 w-3.5" />
                  Download
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

function GenerateReportDialog({ onGenerated }: { onGenerated: (r: Report) => void }) {
  const [open, setOpen] = useState(false)
  const [prompt, setPrompt] = useState("")

  function generate() {
    onGenerated({
      id: crypto.randomUUID(),
      title: prompt.trim() || "New report",
      type: "Custom",
      status: "generating",
      generatedAt: "just now",
      format: "Markdown",
    })
    toast.success("Report generation started")
    setOpen(false)
    setPrompt("")
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate report
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate report</DialogTitle>
          <DialogDescription>Describe the report you want the AI to create.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            placeholder="e.g. Summarize incident resolution times for the last 30 days"
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={generate} disabled={!prompt.trim()}>
            Generate
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}