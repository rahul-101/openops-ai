import { useTheme } from "@/components/theme-provider"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"
import { useState } from "react"

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