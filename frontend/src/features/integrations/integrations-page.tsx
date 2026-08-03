import { useQuery } from "@tanstack/react-query"
import { CheckCircle2, Cpu, Plug, Settings2, TerminalSquare, XCircle } from "lucide-react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { EmptyState, LoadingState } from "@/components/shared/states"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"
import { feClient } from "@/services/api"
import { cn, titleCase } from "@/lib/utils"
import type { ProviderMetadata } from "@/types/api"

interface RiskActions {
  [action: string]: string
}

interface ToolGroup {
  tool: string
  actions: { action: string; risk: string }[]
}

const riskStyles: Record<string, string> = {
  low: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600",
  medium: "border-amber-500/30 bg-amber-500/10 text-amber-600",
  high: "border-destructive/30 bg-destructive/10 text-destructive",
}

function groupByTool(risk: RiskActions): ToolGroup[] {
  const map = new Map<string, { action: string; risk: string }[]>()
  for (const [key, riskLevel] of Object.entries(risk)) {
    const parts = key.split(".")
    const tool = parts[1] ?? key
    const action = parts.slice(2).join(".") || key
    if (!map.has(tool)) map.set(tool, [])
    map.get(tool)!.push({ action, risk: riskLevel })
  }
  return [...map.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([tool, actions]) => ({ tool, actions }))
}

export function IntegrationsPage() {
  const risk = useQuery({
    queryKey: ["integrations", "risk"],
    queryFn: () => feClient.get<RiskActions>("/aiops/risk/actions"),
  })
  const providers = useQuery({
    queryKey: ["integrations", "providers"],
    queryFn: () => feClient.get<ProviderMetadata[]>("/providers"),
  })

  const loading = risk.isPending || providers.isPending
  const tools = groupByTool(risk.data ?? {})
  const enabledProviders = (providers.data ?? []).filter((p) => p.enabled)

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Integrations"
        description="Registered remediation tools and the AI providers powering autonomous response."
        eyebrow="Platform"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Remediation tools" value={tools.length} icon={TerminalSquare} accent="primary" hint="registered" />
        <StatCard label="Actions" value={Object.keys(risk.data ?? {}).length} icon={Settings2} accent="accent" hint="risk-gated" />
        <StatCard label="AI providers" value={providers.data?.length ?? 0} icon={Plug} accent="success" hint="catalog" />
        <StatCard label="Enabled" value={enabledProviders.length} icon={CheckCircle2} accent="warning" hint="active models" />
      </div>

      {loading ? (
        <LoadingState label="Loading integrations…" className="mt-4" />
      ) : (
        <>
          <h2 className="mt-8 mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">Remediation tool stack</h2>
          {tools.length === 0 ? (
            <CardShell title="Remediation tools">
              <EmptyState title="No tools registered" description="Register risk-gated tool actions to enable remediation." />
            </CardShell>
          ) : (
            <div className="grid gap-4 lg:grid-cols-3">
              {tools.map((t) => (
                <CardShell
                  key={t.tool}
                  title={titleCase(t.tool)}
                  description="Risk-gated remediation actions"
                  action={<Badge className="border-transparent bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"><CheckCircle2 className="mr-1 h-3 w-3" />Connected</Badge>}
                >
                  <div className="flex flex-wrap gap-1.5">
                    {t.actions.map((a) => (
                      <span key={a.action} className={cn("rounded px-2 py-1 text-[11px] font-medium", riskStyles[a.risk] ?? "bg-muted text-muted-foreground")}>
                        {a.action}
                        <span className="ml-1.5 text-[10px] uppercase opacity-70">{a.risk}</span>
                      </span>
                    ))}
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <Button size="sm" variant="ghost" onClick={() => toast.info(`Configure ${titleCase(t.tool)}`)}>
                      Configure
                    </Button>
                    <Switch defaultChecked onCheckedChange={() => toast.success("Integration toggled")} aria-label={`Toggle ${t.tool}`} />
                  </div>
                </CardShell>
              ))}
            </div>
          )}

          <h2 className="mt-8 mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">AI model providers</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {(providers.data ?? []).map((p) => (
              <CardShell
                key={p.name}
                title={p.display_name ?? titleCase(p.name)}
                description={`Priority ${p.priority} · ${p.max_context_tokens.toLocaleString()} token context`}
                action={
                  <Badge variant={p.enabled ? "default" : "secondary"}>{p.enabled ? "Enabled" : "Disabled"}</Badge>
                }
              >
                <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-violet-500/15 text-violet-500">
                    <Cpu className="h-5 w-5" />
                  </span>
                  <div className="flex-1">
                    <p className="font-mono text-xs text-muted-foreground">{p.model}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      ${(p.input_cost_per_1k_tokens * 1000).toFixed(4)}/1M in · ${(p.output_cost_per_1k_tokens * 1000).toFixed(4)}/1M out
                    </p>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1">
                  {p.capabilities.slice(0, 4).map((c) => (
                    <Badge key={c} variant="outline" className="text-[10px] capitalize">
                      {c.replace(/_/g, " ")}
                    </Badge>
                  ))}
                </div>
              </CardShell>
            ))}
          </div>
          {providers.data && providers.data.length === 0 && (
            <CardShell title="AI providers">
              <EmptyState icon={XCircle} title="No providers" description="Register an AI provider to enable autonomous decisioning." />
            </CardShell>
          )}
        </>
      )}
    </div>
  )
}
