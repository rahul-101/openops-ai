import { CheckCircle2, Link2, Plug, Settings2, XCircle } from "lucide-react"
import { useState } from "react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"

interface Integration {
  id: string
  name: string
  category: string
  description: string
  connected: boolean
  icon: string
  health: "healthy" | "degraded" | "disconnected"
}

const seedIntegrations: Integration[] = [
  { id: "i1", name: "ServiceNow", category: "Ticketing", description: "Incident and change management", connected: true, icon: "snow", health: "healthy" },
  { id: "i2", name: "Jira", category: "Ticketing", description: "Issue tracking and project boards", connected: true, icon: "jira", health: "healthy" },
  { id: "i3", name: "AWS", category: "Cloud", description: "EC2, Lambda and S3 remediation", connected: true, icon: "aws", health: "degraded" },
  { id: "i4", name: "Kubernetes", category: "Infrastructure", description: "Pods, deployments and autoscaling", connected: true, icon: "k8s", health: "healthy" },
  { id: "i5", name: "Slack", category: "Communications", description: "Incident alerts and channels", connected: true, icon: "slack", health: "healthy" },
  { id: "i6", name: "Microsoft Teams", category: "Communications", description: "Team notifications and approvals", connected: false, icon: "teams", health: "disconnected" },
  { id: "i7", name: "Azure", category: "Cloud", description: "Virtual machines and resources", connected: false, icon: "azure", health: "disconnected" },
  { id: "i8", name: "Prometheus", category: "Monitoring", description: "Metrics and alert ingestion", connected: true, icon: "prom", health: "healthy" },
]

const iconColors: Record<string, string> = {
  snow: "bg-sky-500/15 text-sky-500",
  jira: "bg-blue-500/15 text-blue-500",
  aws: "bg-amber-500/15 text-amber-500",
  k8s: "bg-indigo-500/15 text-indigo-500",
  slack: "bg-purple-500/15 text-purple-500",
  teams: "bg-violet-500/15 text-violet-500",
  azure: "bg-cyan-500/15 text-cyan-500",
  prom: "bg-orange-500/15 text-orange-500",
}

export function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>(seedIntegrations)

  const connected = integrations.filter((i) => i.connected).length
  const degraded = integrations.filter((i) => i.health === "degraded").length

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Integrations"
        description="Connect OpenOps AI to your observability, cloud and communication stack."
        eyebrow="Platform"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Integrations" value={integrations.length} icon={Plug} accent="primary" hint="available" />
        <StatCard label="Connected" value={connected} icon={Link2} accent="success" hint="active" />
        <StatCard label="Degraded" value={degraded} icon={XCircle} accent="warning" hint="needs attention" />
        <StatCard label="Disconnected" value={integrations.length - connected} icon={Settings2} accent="default" hint="available to connect" />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {integrations.map((i) => (
          <CardShell key={i.id} title={i.name} action={<HealthBadge health={i.health} />}>
            <div className="flex items-start gap-3">
              <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${iconColors[i.icon] ?? "bg-muted text-muted-foreground"}`}>
                <Plug className="h-5 w-5" />
              </span>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">{i.category}</p>
                <p className="mt-0.5 text-sm text-muted-foreground/80">{i.description}</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <Button size="sm" variant="ghost" onClick={() => toast.info(`Configure ${i.name}`)}>
                Configure
              </Button>
              <Switch
                checked={i.connected}
                onCheckedChange={(checked) => {
                  setIntegrations((prev) =>
                    prev.map((x) => (x.id === i.id ? { ...x, connected: checked, health: checked ? "healthy" : "disconnected" } : x)),
                  )
                  toast.success(`${i.name} ${checked ? "connected" : "disconnected"}`)
                }}
                aria-label={`Toggle ${i.name}`}
              />
            </div>
          </CardShell>
        ))}
      </div>
    </div>
  )
}

function HealthBadge({ health }: { health: Integration["health"] }) {
  const map = {
    healthy: "border-transparent bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
    degraded: "border-transparent bg-amber-500/15 text-amber-600 dark:text-amber-400",
    disconnected: "border-transparent bg-muted text-muted-foreground",
  } as const
  return (
    <Badge className={map[health]}>
      {health === "healthy" && <CheckCircle2 className="mr-1 h-3 w-3" />}
      {health === "degraded" && <XCircle className="mr-1 h-3 w-3" />}
      {health}
    </Badge>
  )
}