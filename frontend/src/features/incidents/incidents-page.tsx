import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus, Search } from "lucide-react"
import { useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { PageHeader } from "@/components/shared/page-header"
import { ErrorState } from "@/components/shared/states"
import { SeverityBadge, StatusBadge } from "@/components/shared/status-badges"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { incidentKeys, createIncident, useIncidents } from "./hooks"
import { CreateIncidentDialog } from "./create-incident-dialog"
import { Reveal } from "@/components/shared/motion"
import { formatRelativeTime } from "@/lib/utils"
import type { IncidentSeverity, IncidentStatus } from "@/types/api"

const severities: IncidentSeverity[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
const statuses: IncidentStatus[] = ["OPEN", "IN_PROGRESS", "RESOLVED"]

export function IncidentsPage() {
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState<IncidentStatus | "ALL">("ALL")
  const [severity, setSeverity] = useState<IncidentSeverity | "ALL">("ALL")
  const [page, setPage] = useState(1)

  const incidents = useIncidents({
    page,
    size: 20,
    status: status === "ALL" ? undefined : status,
    severity: severity === "ALL" ? undefined : severity,
    search: search || undefined,
  })

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Incidents"
        description="Track incidents from detection through autonomous resolution."
        eyebrow="Operations"
        action={<CreateIncidentButton />}
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            placeholder="Search incidents…"
            className="pl-9"
          />
        </div>
        <Select
          value={status}
          onValueChange={(v) => {
            setStatus(v as IncidentStatus | "ALL")
            setPage(1)
          }}
        >
          <SelectTrigger className="w-full sm:w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All statuses</SelectItem>
            {statuses.map((s) => (
              <SelectItem key={s} value={s}>
                {s.replace("_", " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={severity}
          onValueChange={(v) => {
            setSeverity(v as IncidentSeverity | "ALL")
            setPage(1)
          }}
        >
          <SelectTrigger className="w-full sm:w-[150px]">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All severities</SelectItem>
            {severities.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {incidents.isPending ? (
        <IncidentTableSkeleton />
      ) : incidents.isError ? (
        <ErrorState message={incidents.error.message} onRetry={() => incidents.refetch()} />
      ) : (
        <Reveal>
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Source</TableHead>
                <TableHead className="text-right">Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(incidents.data?.items ?? []).length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-40 text-center text-sm text-muted-foreground">
                    {search || status !== "ALL" || severity !== "ALL"
                      ? "No incidents match your filters."
                      : "No incidents yet. Create your first incident to get started."}
                  </TableCell>
                </TableRow>
              ) : (
                incidents.data!.items.map((inc) => (
                  <TableRow key={inc.id} className="cursor-pointer">
                    <TableCell>
                      <Link to={`/incidents/${inc.id}`} className="block">
                        <span className="font-medium hover:text-primary">{inc.title}</span>
                        <span className="block text-xs text-muted-foreground">{inc.id.slice(0, 8)}</span>
                      </Link>
                    </TableCell>
                    <TableCell>
                      <SeverityBadge severity={inc.severity} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={inc.status} />
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{inc.source}</TableCell>
                    <TableCell className="text-right text-sm tabular-nums text-muted-foreground">
                      {formatRelativeTime(inc.updated_at)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {(incidents.data?.total_pages ?? 0) > 1 && (
            <PaginationControls
              page={page}
              totalPages={incidents.data!.total_pages}
              onPageChange={setPage}
            />
          )}
        </div>
        </Reveal>
      )}
    </div>
  )
}

function PaginationControls({
  page,
  totalPages,
  onPageChange,
}: {
  page: number
  totalPages: number
  onPageChange: (p: number) => void
}) {
  return (
    <div className="flex items-center justify-between border-t bg-muted/20 px-4 py-2.5">
      <p className="text-xs text-muted-foreground">
        Page {page} of {totalPages}
      </p>
      <div className="flex gap-1">
        <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </Button>
        <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Next
        </Button>
      </div>
    </div>
  )
}

function CreateIncidentButton() {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: createIncident,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: incidentKeys.all })
      toast.success("Incident created")
    },
    onError: (err) => toast.error(err.message),
  })
  return (
    <CreateIncidentDialog onSubmit={mutation.mutate} busy={mutation.isPending}>
      <Button>
        <Plus className="mr-2 h-4 w-4" />
        New incident
      </Button>
    </CreateIncidentDialog>
  )
}

function IncidentTableSkeleton() {
  return (
    <div className="overflow-hidden rounded-lg border">
      <div className="border-b bg-muted/20 px-4 py-3">
        <Skeleton className="h-4 w-40" />
      </div>
      <div className="divide-y">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-4 py-3.5">
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-5 w-24" />
            <Skeleton className="ml-auto h-4 w-24" />
          </div>
        ))}
      </div>
    </div>
  )
}