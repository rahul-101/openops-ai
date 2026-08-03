import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { CheckCircle2, Clock, Play, ShieldCheck, XCircle } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { feClient } from "@/services/api"
import { cn, formatDateTime, formatRelativeTime, titleCase } from "@/lib/utils"
import type { Approval, ApprovalStatus } from "@/types/api"

const approvalsKeys = {
  all: ["approvals"] as const,
  pending: ["approvals", "pending"] as const,
  history: ["approvals", "history"] as const,
}

export function ApprovalsPage() {
  const pending = useQuery({
    queryKey: approvalsKeys.pending,
    queryFn: () => feClient.get<Approval[]>("/approvals/pending"),
  })
  const history = useQuery({
    queryKey: approvalsKeys.history,
    queryFn: () => feClient.get<Approval[]>("/approvals/history"),
  })

  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: approvalsKeys.all })

  const approve = useMutation({
    mutationFn: (id: string) => feClient.post<Approval>(`/approvals/${id}/approve`, { approved_by: "operator" }),
    onSuccess: () => {
      toast.success("Approval granted")
      invalidate()
    },
    onError: (err) => toast.error(err.message),
  })

  const reject = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      feClient.post<Approval>(`/approvals/${id}/reject`, { approved_by: "operator", reason }),
    onSuccess: () => {
      toast.success("Approval rejected")
      invalidate()
    },
    onError: (err) => toast.error(err.message),
  })

  const execute = useMutation({
    mutationFn: (id: string) => feClient.post<{ success: boolean; data: Record<string, unknown>; error: string | null }>(`/approvals/${id}/execute`),
    onSuccess: (res) => {
      if (res.success) toast.success("Remediation action executed")
      else toast.error(res.error ?? "Execution failed")
      invalidate()
    },
    onError: (err) => toast.error(err.message),
  })

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Approvals"
        description="Review and authorize risky remediation actions proposed by the autonomous pipeline."
        eyebrow="Automation"
        action={<PendingCount count={pending.data?.length ?? 0} />}
      />

      <Tabs defaultValue="pending">
        <TabsList>
          <TabsTrigger value="pending">
            Pending
            {(pending.data?.length ?? 0) > 0 && (
              <span className="ml-2 rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                {pending.data!.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="pending">
          <PendingTab
            loading={pending.isPending}
            items={pending.data ?? []}
            approving={approve.isPending}
            rejecting={reject.isPending}
            executing={execute.isPending}
            onApprove={(id) => approve.mutate(id)}
            onReject={(id, reason) => reject.mutate({ id, reason })}
            onExecute={(id) => execute.mutate(id)}
          />
        </TabsContent>

        <TabsContent value="history">
          <HistoryTab loading={history.isPending} items={history.data ?? []} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function PendingCount({ count }: { count: number }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-600 ring-1 ring-inset ring-amber-500/20">
      <Clock className="h-3.5 w-3.5" />
      {count} awaiting review
    </span>
  )
}

function PendingTab({
  loading,
  items,
  approving,
  rejecting,
  executing,
  onApprove,
  onReject,
  onExecute,
}: {
  loading: boolean
  items: Approval[]
  approving: boolean
  rejecting: boolean
  executing: boolean
  onApprove: (id: string) => void
  onReject: (id: string, reason?: string) => void
  onExecute: (id: string) => void
}) {
  if (loading) return <LoadingState label="Loading pending approvals…" />
  if (!items.length)
    return (
      <CardShell title="Pending approvals" description="Nothing waiting on a human decision">
        <EmptyState
          icon={ShieldCheck}
          title="Queue is clear"
          description="All risky actions have been reviewed or executed."
        />
      </CardShell>
    )

  return (
    <div className="space-y-3">
      {items.map((approval) => (
        <PendingCard
          key={approval.id}
          approval={approval}
          approving={approving}
          rejecting={rejecting}
          executing={executing}
          onApprove={() => onApprove(approval.id)}
          onReject={(reason) => onReject(approval.id, reason)}
          onExecute={() => onExecute(approval.id)}
        />
      ))}
    </div>
  )
}

function PendingCard({
  approval,
  approving,
  rejecting,
  executing,
  onApprove,
  onReject,
  onExecute,
}: {
  approval: Approval
  approving: boolean
  rejecting: boolean
  executing: boolean
  onApprove: () => void
  onReject: (reason?: string) => void
  onExecute: () => void
}) {
  const [rejectOpen, setRejectOpen] = useState(false)
  const [reason, setReason] = useState("")
  const [executeOpen, setExecuteOpen] = useState(false)

  const { action, params } = describeParameters(approval.parameters)
  const incidentId = approval.context?.incident_id as string | undefined

  return (
    <CardShell
      title={approval.tool_name.replace(/^tool\./, "")}
      description={`Requested by ${approval.requested_by ?? "system"} · ${formatRelativeTime(approval.created_at)}`}
      action={
        <div className="flex items-center gap-2">
          {approval.status === "approved" ? (
            <Button size="sm" onClick={() => setExecuteOpen(true)} disabled={executing}>
              {executing ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary/30 border-t-primary" /> : <Play className="h-4 w-4" />}
              Execute
            </Button>
          ) : (
            <>
              <Button size="sm" variant="destructive" onClick={() => setRejectOpen(true)} disabled={rejecting}>
                <XCircle className="h-4 w-4" />
                Reject
              </Button>
              <Button size="sm" onClick={onApprove} disabled={approving}>
                {approving ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground" /> : <CheckCircle2 className="h-4 w-4" />}
                Approve
              </Button>
            </>
          )}
        </div>
      }
    >
      <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto]">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ApprovalStatusBadge status={approval.status} />
            {incidentId && <span className="font-mono text-xs text-muted-foreground">{incidentId}</span>}
          </div>
          {action && (
            <div>
              <p className="text-xs font-medium text-muted-foreground">Action</p>
              <p className="font-mono text-sm">{action}</p>
            </div>
          )}
          {params.length > 0 && (
            <div>
              <p className="text-xs font-medium text-muted-foreground">Parameters</p>
              <dl className="mt-1 grid gap-1 font-mono text-sm sm:grid-cols-2">
                {params.map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <dt className="text-muted-foreground">{key}:</dt>
                    <dd className="truncate">{String(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
        <div className="space-y-1 text-right text-xs text-muted-foreground sm:text-left">
          <p>Created {formatRelativeTime(approval.created_at)}</p>
        </div>
      </div>

      <RejectDialog open={rejectOpen} onOpenChange={setRejectOpen} busy={rejecting} onSubmit={() => onReject(reason.trim() || undefined)}>
        <div className="space-y-2 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="reject-reason">Reason (optional)</Label>
            <Input
              id="reject-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. incident already mitigated"
            />
          </div>
        </div>
      </RejectDialog>

      <ExecuteDialog open={executeOpen} onOpenChange={setExecuteOpen} busy={executing} onConfirm={onExecute} />
    </CardShell>
  )
}

function HistoryTab({ loading, items }: { loading: boolean; items: Approval[] }) {
  if (loading) return <LoadingState label="Loading approval history…" />
  if (!items.length)
    return (
      <CardShell title="Approval history" description="Audit trail of every decision">
        <EmptyState title="No approvals recorded" description="Decisions will appear here as the pipeline requests authorizations." />
      </CardShell>
    )

  const sorted = [...items].sort((a, b) => b.created_at.localeCompare(a.created_at))

  return (
    <CardShell title="Approval history" description="Audit trail of every decision">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tool</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Requested by</TableHead>
              <TableHead>Decided by</TableHead>
              <TableHead>Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((approval) => {
              const { action } = describeParameters(approval.parameters)
              return (
                <TableRow key={approval.id}>
                  <TableCell className="font-medium">{approval.tool_name.replace(/^tool\./, "")}</TableCell>
                  <TableCell className="font-mono text-xs">{action ?? "—"}</TableCell>
                  <TableCell>
                    <ApprovalStatusBadge status={approval.status} />
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">{approval.requested_by ?? "system"}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">{approval.approved_by ?? "—"}</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{formatDateTime(approval.updated_at)}</TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </CardShell>
  )
}

function ApprovalStatusBadge({ status }: { status: ApprovalStatus }) {
  const styles: Record<ApprovalStatus, string> = {
    pending: "border-amber-500/30 bg-amber-500/10 text-amber-600",
    approved: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
    rejected: "border-destructive/30 bg-destructive/10 text-destructive",
    executed: "border-sky-500/30 bg-sky-500/10 text-sky-600",
  }
  return <Badge variant="outline" className={cn("px-2 py-0.5 text-[11px]", styles[status])}>{titleCase(status)}</Badge>
}

function RejectDialog({
  open,
  onOpenChange,
  busy,
  onSubmit,
  children,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  busy: boolean
  onSubmit: () => void
  children: React.ReactNode
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Reject approval</DialogTitle>
          <DialogDescription>The remediation action will not run. The incident will be marked as awaiting manual intervention.</DialogDescription>
        </DialogHeader>
        {children}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={busy}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={onSubmit} disabled={busy}>
            {busy ? "Rejecting…" : "Reject approval"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function ExecuteDialog({
  open,
  onOpenChange,
  busy,
  onConfirm,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  busy: boolean
  onConfirm: () => void
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Execute approved action?</AlertDialogTitle>
          <AlertDialogDescription>
            This will run the approved remediation action against the target system. It cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={busy}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={busy} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
            {busy ? "Executing…" : "Execute"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

function describeParameters(parameters: Record<string, unknown>) {
  const entries = Object.entries(parameters).filter(([, v]) => v !== undefined && v !== null && v !== "")
  const action = entries.find(([k]) => k === "action")?.[1] as string | undefined
  const params = entries.filter(([k]) => k !== "action" && k !== "tool")
  return { action, params }
}
