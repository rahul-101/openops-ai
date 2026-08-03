import { useTheme } from "@/components/theme-provider"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { feClient } from "@/services/api"
import { useQuery } from "@tanstack/react-query"
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