import { useQuery } from "@tanstack/react-query"
import { Bell, CheckCircle2, TriangleAlert } from "lucide-react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { ErrorState, EmptyState } from "@/components/shared/states"
import { SeverityBadge } from "@/components/shared/status-badges"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { IncidentSeverity } from "@/types/api"

interface NormalizedEvent {
  event_id: string
  source: string
  title: string
  severity: IncidentSeverity
  service: string | null
  ingested_at?: string
}

export function AlertsPage() {
  const alerts = useQuery({
    queryKey: ["alerts"],
    queryFn: () => feClient.get<NormalizedEvent[]>("/aiops/events?limit=50"),
    refetchInterval: 10_000,
  })

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Alerts"
        description="Normalized alerts ingested from monitoring systems across your stack."
        eyebrow="Automation"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Alerts" value={alerts.data?.length ?? "—"} icon={Bell} accent="primary" hint="recent" />
        <StatCard label="Critical" value={(alerts.data ?? []).filter((a) => a.severity === "CRITICAL").length} icon={TriangleAlert} accent="destructive" hint="severity" />
        <StatCard label="High" value={(alerts.data ?? []).filter((a) => a.severity === "HIGH").length} icon={TriangleAlert} accent="warning" hint="severity" />
        <StatCard label="Auto-triaged" value="—" icon={CheckCircle2} accent="success" hint="by pipeline" />
      </div>

      <div className="mt-4">
        <CardShell title="Recent alerts" description="Latest normalized alert events">
          {alerts.isPending ? (
            <div className="space-y-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : alerts.isError ? (
            <ErrorState message={alerts.error.message} onRetry={() => alerts.refetch()} />
          ) : !alerts.data?.length ? (
            <EmptyState
              title="No alerts ingested"
              description="Ingest an alert from the Operations page to see it here."
              className="min-h-[280px]"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead className="text-right">Received</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.data.map((a) => (
                  <TableRow key={a.event_id}>
                    <TableCell className="font-medium">{a.title}</TableCell>
                    <TableCell className="text-muted-foreground">{a.source}</TableCell>
                    <TableCell>
                      {a.service ? (
                        <Badge variant="outline">{a.service}</Badge>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <SeverityBadge severity={a.severity} />
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">{a.ingested_at ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardShell>
      </div>
    </div>
  )
}