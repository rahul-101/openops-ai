import { motion } from "framer-motion"
import { BrainCircuit, CheckCircle2, GitBranch, Radar, ShieldCheck, UserCheck, Wrench } from "lucide-react"
import type { LucideIcon } from "lucide-react"

import { fadeUp, viewport } from "./motion"
import { cn } from "@/lib/utils"

interface FlowNode {
  icon: LucideIcon
  title: string
  detail: string
  tone: string
  label?: string
  badge?: string
  badgeTone?: string
}

const MAIN_NODES: FlowNode[] = [
  {
    icon: Radar,
    title: "Ingest & correlate",
    detail: "Alerts from Kubernetes, AWS, Prometheus and ServiceNow are normalized into one incident timeline.",
    tone: "text-chart-1 border-chart-1/30 bg-chart-1/10",
  },
  {
    icon: BrainCircuit,
    title: "Diagnose",
    detail: "Agents pull logs, metrics and deploy history to produce a root cause with confidence score.",
    tone: "text-chart-2 border-chart-2/30 bg-chart-2/10",
  },
  {
    icon: Wrench,
    title: "Plan & remediate",
    detail: "The planner drafts an execution runbook with per-step risk scoring.",
    tone: "text-chart-3 border-chart-3/30 bg-chart-3/10",
  },
]

const BRANCHES = [
  {
    icon: ShieldCheck,
    title: "Low risk · auto-execute",
    detail: "Steps scoring under the auto-approve threshold run immediately, then verify the fix is healthy.",
    tone: "text-success border-success/30 bg-success/10",
    badge: "~95% of steps",
    badgeTone: "bg-success/15 text-success",
  },
  {
    icon: UserCheck,
    title: "High risk · human approval",
    detail: "Destructive or cross-service changes are gated behind one-click approval — engineers stay in control.",
    tone: "text-warning border-warning/30 bg-warning/10",
    badge: "gated & audited",
    badgeTone: "bg-warning/15 text-warning",
  },
]

function Arrow({ className }: { className?: string }) {
  return (
    <div className={cn("flex justify-center py-1", className)} aria-hidden>
      <motion.svg
        width="20"
        height="24"
        viewBox="0 0 20 24"
        fill="none"
        animate={{ y: [0, 4, 0] }}
        transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
      >
        <path d="M10 1v20" stroke="hsl(var(--chart-2)/0.6)" strokeWidth="2" strokeLinecap="round" strokeDasharray="3 5" />
        <path d="M4 16l6 7 6-7" stroke="hsl(var(--chart-2))" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      </motion.svg>
    </div>
  )
}

function BranchArrow() {
  return (
    <div className="relative flex items-center justify-center" aria-hidden>
      <div className="h-10 w-px border-l-2 border-dashed border-chart-2/40" />
    </div>
  )
}

function FlowCard({ node, index }: { node: FlowNode; index: number }) {
  const Icon = node.icon
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      initial="hidden"
      whileInView="visible"
      viewport={viewport}
      className="glass-card rounded-xl p-5 text-center sm:p-6"
    >
      <div className={cn("mx-auto flex h-12 w-12 items-center justify-center rounded-xl border", node.tone)}>
        <Icon className="h-6 w-6" />
      </div>
      <p className="mt-3 text-sm font-semibold">{node.title}</p>
      <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{node.detail}</p>
    </motion.div>
  )
}

function BranchCard({ node, index }: { node: FlowNode; index: number }) {
  const Icon = node.icon
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      initial="hidden"
      whileInView="visible"
      viewport={viewport}
      className="relative flex h-full flex-col rounded-xl border bg-background/60 p-5"
    >
      <div className="flex items-center justify-between">
        <div className={cn("flex h-11 w-11 items-center justify-center rounded-xl border", node.tone)}>
          <Icon className="h-5 w-5" />
        </div>
        <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-semibold", node.badgeTone)}>{node.badge}</span>
      </div>
      <p className="mt-3 text-sm font-semibold">{node.title}</p>
      <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{node.detail}</p>
    </motion.div>
  )
}

export function LandingFlow() {
  return (
    <section id="flow" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto max-w-2xl text-center"
      >
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">End-to-end pipeline</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-5xl">
          One incident,{" "}
          <span className="text-gradient">three agents, zero wake-ups</span>
        </h2>
        <p className="mt-4 text-muted-foreground">
          Follow the lifecycle from raw alert to verified resolution — and where the risk gate keeps a human in the loop.
        </p>
      </motion.div>

      {/* Main pipeline */}
      <div className="relative mt-16 grid gap-3 md:grid-cols-[1fr_auto_1fr_auto_1fr] md:items-center">
        {MAIN_NODES.map((node, i) => (
          <div key={node.title} className="contents">
            <FlowCard node={node} index={i} />
            {i < MAIN_NODES.length - 1 && <Arrow className="hidden md:flex" />}
          </div>
        ))}
        <Arrow className="md:hidden" />
      </div>

      {/* Risk gate branch */}
      <div className="relative mx-auto mt-4 max-w-3xl text-center">
        <motion.div
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={viewport}
          className="inline-flex items-center gap-2 rounded-full border border-chart-2/30 bg-chart-2/10 px-4 py-1.5 text-xs font-medium text-chart-2"
        >
          <GitBranch className="h-3.5 w-3.5" />
          Risk gate · every step scored before it runs
        </motion.div>
      </div>

      <BranchArrow />

      <div className="grid gap-4 md:grid-cols-2">
        {BRANCHES.map((node, i) => (
          <BranchCard key={node.title} node={node} index={i} />
        ))}
      </div>

      <BranchArrow />

      {/* Converge */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto mt-2 max-w-xl"
      >
        <div className="glass-card rounded-xl p-5 text-center sm:p-6">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-chart-4/30 bg-chart-4/10 text-chart-4">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <p className="mt-3 text-sm font-semibold">Verify, close & audit</p>
          <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
            Health checks confirm the fix, the incident closes automatically, and every action — model, prompt,
            approval, outcome — is written to the immutable audit log with cost telemetry.
          </p>
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto mt-8 flex max-w-2xl flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-muted-foreground"
      >
        {[
          { dot: "bg-chart-1", label: "Incident agent" },
          { dot: "bg-chart-2", label: "RCA agent" },
          { dot: "bg-chart-3", label: "Planner agent" },
          { dot: "bg-chart-4", label: "Verification" },
          { dot: "bg-warning", label: "Human approval" },
        ].map((l) => (
          <span key={l.label} className="inline-flex items-center gap-1.5">
            <span className={cn("h-2 w-2 rounded-full", l.dot)} />
            {l.label}
          </span>
        ))}
      </motion.div>

      {/* Note for judges */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto mt-8 max-w-2xl rounded-xl border border-border/60 bg-background/50 p-4 text-center text-xs text-muted-foreground"
      >
        <span className="font-medium text-foreground">Real lifecycle in the app:</span>{" "}
        every incident you see in the dashboard is executed by this exact pipeline and recorded end-to-end.
      </motion.div>
    </section>
  )
}