import { useTheme } from "@/components/theme-provider"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { feClient } from "@/services/api"
import { useMutation, useQuery } from "@tanstack/react-query"
import { Cpu, DollarSign, Gauge, Play, Shield, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { useState } from "react"
import { cn } from "@/lib/utils"
import type { ProviderMetadata } from "@/types/api"

export function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const [orgName, setOrgName] = useState("OpenOps Inc.")
  const [workspace, setWorkspace] = useState("acme-production")
  const [notifications, setNotifications] = useState(true)
  const [autoRemediation, setAutoRemediation] = useState(true)
  const [sso, setSso] = useState(false)

  return (
    <div className="container max-w-4xl px-6 py-8">
      <PageHeader
        title="Settings"
        description="Configure your workspace, preferences and automation policies."
        eyebrow="Platform"
      />

      <div className="space-y-4">
        <CardShell title="Organization" description="Workspace identity and defaults">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="s-org">Organization name</Label>
              <Input id="s-org" value={orgName} onChange={(e) => setOrgName(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="s-ws">Workspace</Label>
              <Input id="s-ws" value={workspace} onChange={(e) => setWorkspace(e.target.value)} />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <Button onClick={() => toast.success("Organization settings saved")}>Save changes</Button>
          </div>
        </CardShell>

        <CardShell title="Appearance" description="Theme preference">
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <p className="text-sm font-medium">Theme</p>
              <p className="text-xs text-muted-foreground">Choose how the dashboard looks</p>
            </div>
            <div className="flex gap-1 rounded-lg border bg-muted/40 p-1">
              {(["light", "dark", "system"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={`rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors ${
                    theme === t ? "bg-background text-foreground shadow-sm" : "text-muted-foreground"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </CardShell>

        <CardShell title="Automation" description="Autonomous response behavior">
          <div className="space-y-2">
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Auto-remediation</p>
                <p className="text-xs text-muted-foreground">Allow low-risk remediations to execute automatically</p>
              </div>
              <Switch checked={autoRemediation} onCheckedChange={setAutoRemediation} />
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Notifications</p>
                <p className="text-xs text-muted-foreground">Email me on critical incidents</p>
              </div>
              <Switch checked={notifications} onCheckedChange={setNotifications} />
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div>
                <p className="text-sm font-medium">Single sign-on</p>
                <p className="text-xs text-muted-foreground">Require SSO for workspace access</p>
              </div>
              <Switch checked={sso} onCheckedChange={setSso} />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <Button variant="outline" onClick={() => toast.success("Preferences updated")}>
              Save preferences
            </Button>
          </div>
        </CardShell>

        <CardShell title="Governance" description="Live risk and model policy from the autonomous pipeline">
          <GovernanceCard />
        </CardShell>

        <CardShell title="Model usage" description="Live cost and latency from the AI gateway">
          <ModelUsageCard />
        </CardShell>

        <CardShell title="Playbooks" description="Remediation playbooks for autonomous response">
          <PlaybookManagementCard />
        </CardShell>

        <CardShell title="Danger zone" description="Irreversible actions">
          <div className="flex items-center justify-between rounded-lg border border-destructive/30 p-3">
            <div>
              <p className="text-sm font-medium">Delete workspace</p>
              <p className="text-xs text-muted-foreground">Permanently remove all incidents, workflows and data</p>
            </div>
            <Button variant="destructive" onClick={() => toast.error("This action requires confirmation")}>
              Delete
            </Button>
          </div>
        </CardShell>
      </div>
    </div>
  )
}

function ModelUsageCard() {
  const modelStats = useQuery({
    queryKey: ["settings", "modelStats"],
    queryFn: () => feClient.get<{ total_requests: number; total_tokens: number; total_cost_usd: number; average_latency_ms: number; providers: Record<string, unknown> }>("/governance/models/stats"),
  })

  if (modelStats.isPending) {
    return <LoadingState label="Loading model usage…" />
  }

  const stats = modelStats.data ?? { total_requests: 0, total_tokens: 0, total_cost_usd: 0, average_latency_ms: 0, providers: {} }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border p-4">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <p className="text-sm text-muted-foreground">Total Requests</p>
        </div>
        <p className="mt-2 text-2xl font-semibold">{stats.total_requests.toLocaleString()}</p>
      </div>
      <div className="rounded-lg border p-4">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-warning" />
          <p className="text-sm text-muted-foreground">Model Costs</p>
        </div>
        <p className="mt-2 text-2xl font-semibold">${stats.total_cost_usd.toFixed(2)}</p>
      </div>
      <div className="rounded-lg border p-4">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-success" />
          <p className="text-sm text-muted-foreground">Avg Latency</p>
        </div>
        <p className="mt-2 text-2xl font-semibold">{stats.average_latency_ms}ms</p>
      </div>
      <div className="rounded-lg border p-4">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-accent" />
          <p className="text-sm text-muted-foreground">Providers</p>
        </div>
        <p className="mt-2 text-2xl font-semibold">{Object.keys(stats.providers).length}</p>
      </div>
    </div>
  )
}

interface Playbook {
  name: string
  version?: string
  steps?: unknown[]
}

function PlaybookManagementCard() {
  const playbooks = useQuery({
    queryKey: ["settings", "playbooks"],
    queryFn: () => feClient.get<Playbook[]>("/aiops/playbooks"),
  })

  const deleteMutation = useMutation({
    mutationFn: (name: string) => feClient.delete<void>(`/governance/playbooks/${name}`),
    onSuccess: () => {
      toast.success("Playbook deleted")
      playbooks.refetch()
    },
    onError: () => toast.error("Failed to delete playbook"),
  })

  if (playbooks.isPending) {
    return <LoadingState label="Loading playbooks…" />
  }

  const playbookCount = playbooks.data?.length ?? 0

  return (
    <div className="space-y-3">
      {playbookCount === 0 ? (
        <EmptyState
          title="No playbooks configured"
          description="Create playbooks to automate incident remediation."
          className="min-h-[120px]"
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {playbooks.data?.slice(0, 4).map((p) => (
            <div key={p.name} className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-2">
                <Play className="h-4 w-4 text-violet-500" />
                <div>
                  <p className="text-sm font-medium">{p.name}</p>
                  <p className="text-xs text-muted-foreground">{p.steps?.length || 0} steps</p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <Badge variant="outline" className="px-2 py-0.5 text-[10px]">{p.version}</Badge>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 text-muted-foreground hover:text-destructive"
                  onClick={() => deleteMutation.mutate(p.name)}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))}
          {playbookCount > 4 && (
            <div className="col-span-full text-center">
              <p className="text-xs text-muted-foreground">+{playbookCount - 4} more playbooks</p>
            </div>
          )}
        </div>
      )}
      <div className="pt-2">
        <Button variant="outline" className="w-full" onClick={() => window.location.href = "/playbooks"}>
          Manage Playbooks
        </Button>
      </div>
    </div>
  )
}

const riskStyles: Record<string, string> = {
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-600",
  high: "border-destructive/30 bg-destructive/10 text-destructive",
}

function GovernanceCard() {
  const policy = useQuery({
    queryKey: ["settings", "policy"],
    queryFn: () => feClient.get<Record<string, string>>("/governance/approval-policy/actions"),
  })
  const providers = useQuery({
    queryKey: ["settings", "providers"],
    queryFn: () => feClient.get<ProviderMetadata[]>("/providers"),
  })

  const entries = Object.entries(policy.data ?? {})

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Action risk policy</p>
        <div className="divide-y rounded-lg border">
          {entries.length === 0 && <p className="px-3 py-2 text-sm text-muted-foreground">Loading policy…</p>}
          {entries.map(([action, risk]) => (
            <div key={action} className="flex items-center justify-between px-3 py-2">
              <span className="font-mono text-xs">{action}</span>
              <Badge variant="outline" className={cn("px-2 py-0.5 text-[10px]", riskStyles[risk] ?? "bg-muted text-muted-foreground")}>
                {risk}
              </Badge>
            </div>
          ))}
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Active model providers</p>
        <div className="space-y-2">
          {(providers.data ?? []).map((p) => (
            <div key={p.name} className="flex items-center justify-between rounded-lg border p-3">
              <div className="min-w-0">
                <p className="text-sm font-medium">{p.display_name ?? p.name}</p>
                <p className="truncate font-mono text-xs text-muted-foreground">{p.model}</p>
              </div>
              <Badge variant={p.enabled ? "default" : "secondary"}>{p.enabled ? "Enabled" : "Disabled"}</Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
