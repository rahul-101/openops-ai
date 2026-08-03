import { Gauge, ShieldCheck, Zap } from "lucide-react"

import { ContainerScroll } from "@/components/ui/container-scroll-animation"
import { LogoMark } from "@/components/shared/logo"

export function HeroScrollDemo() {
  return (
    <ContainerScroll
      titleComponent={
        <>
          <p className="mx-auto mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-medium text-primary">
            <Zap className="h-3.5 w-3.5" />
            Autonomous Incident Response
          </p>
          <h1 className="font-display text-4xl font-semibold text-foreground dark:text-white md:text-6xl">
            Run operations <br />
            <span className="bg-gradient-to-r from-primary via-accent to-chart-3 bg-clip-text font-bold text-transparent">
              on autopilot
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-balance text-sm text-muted-foreground md:text-base">
            OpenOps AI ingests alerts, reasons across agents, and executes
            risk-gated remediation — all while you watch the live feed.
          </p>
        </>
      }
    >
      <LiveDashboardPreview />
    </ContainerScroll>
  )
}

function LiveDashboardPreview() {
  const bars = [34, 52, 41, 68, 58, 76, 64, 88, 72, 94, 80, 97]

  return (
    <div className="flex h-full flex-col gap-3 bg-background/95 p-4 text-foreground md:gap-4 md:p-5">
      {/* Preview window chrome */}
      <div className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2">
        <span className="flex gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/70" />
        </span>
        <div className="flex flex-1 items-center justify-center">
          <span className="rounded-md bg-muted px-3 py-0.5 text-[10px] text-muted-foreground">
            app.openops.ai/dashboard
          </span>
        </div>
      </div>

      <div className="grid flex-1 grid-cols-2 gap-3 md:grid-cols-3">
        <div className="col-span-2 space-y-2 md:col-span-2">
          <div className="rounded-lg border bg-card p-3 md:p-4">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Incident throughput
              </p>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-500">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
                Live
              </span>
            </div>
            <div className="mt-3 flex h-24 items-end gap-1.5 md:h-32">
              {bars.map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-sm bg-gradient-to-t from-primary/30 to-primary"
                  style={{ height: `${h}%`, opacity: 0.35 + (i / bars.length) * 0.65 }}
                />
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MiniStat label="Auto-resolved" value="92%" icon={ShieldCheck} tone="emerald" />
            <MiniStat label="Open incidents" value="14" icon={Gauge} tone="amber" />
          </div>
        </div>

        <div className="col-span-2 space-y-2 md:col-span-1">
          <div className="rounded-lg border bg-card p-3 md:p-4">
            <div className="flex items-center gap-2">
              <LogoMark className="h-5 w-5 rounded-md" />
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Agent pipeline
              </p>
            </div>
            <div className="mt-3 space-y-2">
              {["Analyze", "Decide", "Execute", "Verify"].map((stage, i) => (
                <div key={stage} className="flex items-center gap-2">
                  <span
                    className={`flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold ${
                      i < 3
                        ? "bg-primary/15 text-primary"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {i < 3 ? "✓" : i + 1}
                  </span>
                  <span className="flex-1 text-[10px] text-muted-foreground">{stage}</span>
                  {i < 3 && (
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border bg-card p-3 md:p-4">
            <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
              Uptime
            </p>
            <p className="mt-1 font-display text-2xl font-semibold text-emerald-500">99.98%</p>
            <p className="text-[10px] text-muted-foreground">last 90 days</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function MiniStat({
  label,
  value,
  icon: Icon,
  tone,
}: {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  tone: "emerald" | "amber"
}) {
  const tones = {
    emerald: "bg-emerald-500/10 text-emerald-500",
    amber: "bg-amber-500/10 text-amber-500",
  }
  return (
    <div className="rounded-lg border bg-card p-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
          {label}
        </p>
        <span className={`flex h-5 w-5 items-center justify-center rounded-md ${tones[tone]}`}>
          <Icon className="h-3 w-3" />
        </span>
      </div>
      <p className="mt-1 font-display text-xl font-semibold">{value}</p>
    </div>
  )
}
