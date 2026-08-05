import { motion } from "framer-motion"
import { Activity, Bot, CheckCircle2, ShieldCheck, Zap } from "lucide-react"

import { cn } from "@/lib/utils"
import { EASE } from "./motion"

function PanelCard({
  className,
  children,
  delay,
}: {
  className?: string
  children: React.ReactNode
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, y: 24 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.9, ease: EASE, delay: delay ?? 0.4 }}
      className={cn("absolute w-56", className)}
    >
      <motion.div
        animate={{ y: [-8, 8] }}
        transition={{ duration: 6 + (delay ?? 0) * 4, repeat: Infinity, ease: "easeInOut", delay: (delay ?? 0) * 2 }}
        className="glass-card rounded-xl p-3 shadow-[0_20px_50px_-20px_hsl(var(--chart-1)/0.35)]"
      >
        {children}
      </motion.div>
    </motion.div>
  )
}

export function HeroVisual() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10 hidden lg:block" aria-hidden>
      {/* Connecting dashed lines echoing the neural net */}
      <svg className="absolute inset-x-0 top-0 h-1/2 w-full" preserveAspectRatio="none" viewBox="0 0 1000 400" fill="none">
        <path
          d="M120 90 C 260 60, 340 60, 500 110 S 760 180, 890 130"
          stroke="hsl(var(--border)/0.6)"
          strokeWidth="1.5"
          strokeDasharray="6 8"
        />
        <path
          d="M100 300 C 260 260, 360 340, 520 300 S 740 250, 900 300"
          stroke="hsl(var(--border)/0.5)"
          strokeWidth="1.5"
          strokeDasharray="6 8"
        />
      </svg>

      {/* Risk gate card */}
      <PanelCard className="left-[4%] top-[18%]" delay={0.5}>
        <div className="flex items-center justify-between">
          <p className="text-[11px] font-semibold">Risk gate</p>
          <span className="rounded-md bg-success/15 px-1.5 py-0.5 text-[9px] font-semibold text-success">auto-approve</span>
        </div>
        <div className="mt-2 flex items-center gap-2 rounded-lg border border-border/60 bg-background/40 p-2">
          <ShieldCheck className="h-4 w-4 text-chart-3" />
          <div className="flex-1">
            <p className="font-mono text-[10px] leading-tight">restart payments-api</p>
            <p className="mt-0.5 flex items-center gap-1 text-[9px] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-success" /> risk 2/10 · executed
            </p>
          </div>
        </div>
      </PanelCard>

      {/* Timeline status card */}
      <PanelCard className="right-[5%] top-[14%]" delay={0.7}>
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-chart-2" />
          <p className="text-[11px] font-semibold">RCA agent reading</p>
        </div>
        <div className="mt-2 space-y-1.5">
          {[
            { label: "logs", active: true },
            { label: "metrics", active: true },
            { label: "deploy history", active: false },
          ].map((r) => (
            <div key={r.label} className="flex items-center gap-2">
              <span className={cn("h-1.5 w-1.5 rounded-full", r.active ? "bg-chart-2" : "bg-muted-foreground/40")} />
              <p className="font-mono text-[10px] text-muted-foreground">{r.label}</p>
              {r.active && <Activity className="ml-auto h-3 w-3 text-chart-2" />}
            </div>
          ))}
        </div>
      </PanelCard>

      {/* Resolved card */}
      <PanelCard className="bottom-[16%] left-[10%]" delay={0.9}>
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-success" />
          <p className="text-[11px] font-semibold">Incident resolved</p>
        </div>
        <p className="mt-2 flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground">
          <Zap className="h-3 w-3 text-warning" /> MTTR&nbsp;
          <span className="font-semibold text-foreground">42s</span>
          <span className="text-success">(-97%)</span>
        </p>
      </PanelCard>

      {/* Governance card */}
      <PanelCard className="bottom-[26%] right-[9%]" delay={1.1}>
        <div className="flex items-center justify-between">
          <p className="text-[11px] font-semibold">Audit trail</p>
          <span className="text-[9px] text-muted-foreground">live</span>
        </div>
        <div className="mt-2 font-mono text-[10px] leading-relaxed text-muted-foreground">
          <p>14:02:44 <span className="text-chart-2">rollback</span> ✓ approved</p>
          <p>14:02:31 <span className="text-chart-3">root-cause</span> ✓ logged</p>
          <p>14:02:14 <span className="text-chart-1">correlated</span> 6 events</p>
        </div>
      </PanelCard>
    </div>
  )
}