import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus, Search, Play, Trash2 } from "lucide-react"
import { useState } from "react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { ErrorState, EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useDebounceValue } from "@/hooks/use-hooks"
import { titleCase } from "@/lib/utils"
import type { Playbook } from "@/types/api"

const RISK_STYLES = {
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-600",
  high: "border-destructive/30 bg-destructive/10 text-destructive",
}

export function PlaybooksPage() {
  const [search, setSearch] = useState("")
  const debounced = useDebounceValue(search, 400)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [yamlContent, setYamlContent] = useState("")

  const queryClient = useQueryClient()

  const playbooks = useQuery({
    queryKey: ["playbooks"],
    queryFn: () => feClient.get<Playbook[]>("/aiops/playbooks"),
  })

  const saveMutation = useMutation({
    mutationFn: (content: string) =>
      feClient.post<any>("/governance/playbooks", { yaml_content: content }).then(r => r.data),
    onSuccess: () => {
      setIsCreateDialogOpen(false)
      setYamlContent("")
      queryClient.invalidateQueries({ queryKey: ["playbooks"] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (name: string) => feClient.delete<void>(`/governance/playbooks/${name}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["playbooks"] })
    },
  })

  const filtered = (playbooks.data ?? []).filter(p =>
    p.name.toLowerCase().includes(debounced.toLowerCase()) ||
    p.description.toLowerCase().includes(debounced.toLowerCase())
  )

  return (
    <div className="mx-auto w-full max-w-[1600px] px-6 py-8">
      <PageHeader
        title="Playbook Management"
        description="Manage remediation workflows and automation playbooks for incidents."
        eyebrow="Automation"
        action={
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create playbook
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create new playbook</DialogTitle>
                <DialogDescription>
                  Add a new remediation playbook using YAML. It will match against events based on source, severity and tags.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-2">
                <div className="space-y-1.5">
                  <Label htmlFor="yaml-title">YAML Content</Label>
                  <Textarea
                    id="yaml-content"
                    value={yamlContent}
                    onChange={(e) => setYamlContent(e.target.value)}
                    rows={12}
                    placeholder={`name: example-playbook
description: Example remediation playbook
version: 1.0.0
match:
  source: kubernetes
  severities:
    - high
  tags:
    - crash
steps:
  - name: check_pod_status
    tool: kubernetes
    action: pod_status
    risk_level: low
    auto_execute: true
  - name: restart_deployment
    tool: kubernetes
    action: restart
    risk_level: medium
    auto_execute: false`}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => saveMutation.mutate(yamlContent)}
                  disabled={!yamlContent.trim() || saveMutation.isPending}
                >
                  {saveMutation.isPending ? "Creating…" : "Create"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="mb-4 relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search playbooks by name or description…"
          className="pl-9"
        />
      </div>

      <CardShell title={debounced ? `Results for "${debounced}"` : "Registered playbooks"} description={debounced ? "Search results" : "Available remediation workflows"}>
        {playbooks.isPending ? (
          <LoadingState label="Loading playbooks…" className="min-h-[240px]" />
        ) : playbooks.isError ? (
          <ErrorState message="Failed to load playbooks" onRetry={() => playbooks.refetch()} className="min-h-[240px]" />
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No playbooks found"
            description={debounced ? `No matches for "${debounced}".` : "Create a playbook to get started."}
            className="min-h-[240px]"
          />
        ) : (
          <div className="grid gap-3 lg:grid-cols-2">
            {filtered.map((p) => (
              <div key={p.name} className="rounded-lg border p-4">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Play className="h-4 w-4 text-violet-500" />
                    <p className="text-sm font-medium truncate">{p.name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={`px-2 py-0.5 text-[10px] ${RISK_STYLES.low}`}>{p.version}</Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => deleteMutation.mutate(p.name)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
                <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{p.steps.length} step{p.steps.length !== 1 ? "s" : ""}</span>
                  <Badge variant="outline">{titleCase(p.steps[0]?.risk_level || "medium")}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardShell>
    </div>
  )
}
