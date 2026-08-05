import { motion } from "framer-motion"
import { Boxes, BrainCircuit, Cloud, Lock, ShieldCheck } from "lucide-react"

import { Marquee } from "./marquee"
import { fadeUp, staggerContainer, viewport } from "./motion"
import { cn } from "@/lib/utils"

const LAYERS = [
  {
    icon: Cloud,
    name: "Ingest & Normalize",
    tone: "text-chart-1 border-chart-1/30 bg-chart-1/10",
    items: ["Kubernetes", "AWS CloudWatch", "ServiceNow", "Prometheus", "PagerDuty", "Datadog", "Grafana"],
  },
  {
    icon: BrainCircuit,
    name: "Intelligence agents",
    tone: "text-chart-2 border-chart-2/30 bg-chart-2/10",
    items: ["Incident Agent", "RCA Agent", "Planner Agent", "LLM Router", "Knowledge Base", "Semantic Search"],
  },
  {
    icon: Boxes,
    name: "Automation engine",
    tone: "text-chart-3 border-chart-3/30 bg-chart-3/10",
    items: ["Risk Scoring", "Playbooks", "Human Approvals", "Tool Executor", "Verification", "Auto Rollback"],
  },
  {
    icon: Lock,
    name: "Governance & audit",
    tone: "text-chart-4 border-chart-4/30 bg-chart-4/10",
    items: ["Audit Log", "RBAC", "Approval Policy", "Model Governance", "Cost Telemetry", "Reports"],
  },
]

const METRICS = [
  {
    label: "Triage accuracy",
    value: "99.99%",
    note: "across 180k+ incidents",
    render: <LineChart />,
  },
  {
    label: "Autonomous agents",
    value: "3",
    note: "detect · diagnose · remediate",
    render: <StackBars />,
  },
  {
    label: "Self-resolved incidents",
    value: "86%",
    note: "no human touchpoint",
    render: <Donut value={86} />,
  },
  {
    label: "Avg. response time",
    value: "42s",
    note: "from alert to action",
    render: <GaugeMeter />,
  },
]

function LineChart() {
  return (
    <svg viewBox="0 0 120 48" className="h-16 w-full" fill="none" aria-hidden>
      <motion.path
        d="M2 42 C 14 40, 20 34, 30 34 S 46 30, 56 26 S 72 20, 82 18 S 104 12, 118 6"
        stroke="hsl(var(--chart-1))"
        strokeWidth="2.5"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.4, ease: "easeInOut" }}
      />
      <motion.path
        d="M2 42 L118 6"
        stroke="hsl(var(--chart-1))"
        strokeWidth="1"
        strokeDasharray="3 4"
        strokeOpacity="0.4"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.4, ease: "easeInOut", delay: 0.3 }}
      />
    </svg>
  )
}

function StackBars() {
  const bars = [42, 68, 92]
  return (
    <div className="flex h-16 items-end justify-center gap-3">
      {bars.map((h, i) => (
        <motion.span
          key={i}
          initial={{ scaleY: 0 }}
          whileInView={{ scaleY: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: i * 0.12 }}
          style={{ height: `${h}%` }}
          className="w-8 origin-bottom rounded-t-md bg-gradient-to-t from-chart-1 to-chart-2"
        />
      ))}
    </div>
  )
}

function Donut({ value }: { value: number }) {
  const r = 20
  const c = 2 * Math.PI * r
  return (
    <div className="relative mx-auto h-16 w-16">
      <svg viewBox="0 0 48 48" className="h-full w-full -rotate-90" aria-hidden>
        <circle cx="24" cy="24" r={r} fill="none" stroke="hsl(var(--border))" strokeWidth="5" />
        <motion.circle
          cx="24"
          cy="24"
          r={r}
          fill="none"
          stroke="hsl(var(--chart-2))"
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          whileInView={{ strokeDashoffset: c * (1 - value / 100) }}
          viewport={{ once: true }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-display text-sm font-bold">{value}%</span>
    </div>
  )
}

function GaugeMeter() {
  return (
    <div className="mx-auto flex h-16 w-32 items-end justify-center">
      <motion.div
        initial={{ width: 0 }}
        whileInView={{ width: "100%" }}
        viewport={{ once: true }}
        transition={{ duration: 1.3, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        className="h-3 rounded-full bg-gradient-to-r from-chart-4 via-chart-2 to-chart-1"
      />
    </div>
  )
}

function LayerRow({ layer, index }: { layer: (typeof LAYERS)[number]; index: number }) {
  const Icon = layer.icon
  return (
    <motion.div
      initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30, y: 10 }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: index * 0.1 }}
      className="glass-card grid gap-3 rounded-xl p-4 sm:grid-cols-[200px_1fr] sm:items-center"
    >
      <div className="flex items-center gap-3">
        <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border", layer.tone)}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold">{layer.name}</p>
          <p className="text-[11px] text-muted-foreground">Layer 0{index + 1}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {layer.items.map((item, i) => (
          <motion.span
            key={item}
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.25 + index * 0.1 + i * 0.05, duration: 0.4 }}
            className="rounded-md border border-border/70 bg-background/50 px-2.5 py-1 font-mono text-[11px] text-muted-foreground"
          >
            {item}
          </motion.span>
        ))}
      </div>
    </motion.div>
  )
}

const STACK = ["React 18", "TypeScript", "Vite", "Tailwind CSS", "shadcn/ui", "Three.js", "React Query", "Framer Motion", "FastAPI", "Python", "SQLite", "Redis", "Docker", "RBAC"]

export function LandingInfographics() {
  return (
    <section id="architecture" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto max-w-2xl text-center"
      >
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">Inside the system</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-5xl">
          Enterprise architecture,{" "}
          <span className="text-gradient">built to learn</span>
        </h2>
        <p className="mt-4 text-muted-foreground">
          Four layers working together to turn raw signals into verified, audit-ready remediations.
        </p>
      </motion.div>

      {/* Layered architecture */}
      <div className="relative mt-14 space-y-4">
        <div aria-hidden className="absolute bottom-6 left-6 top-6 hidden w-px bg-gradient-to-b from-chart-1 via-chart-2 to-chart-4 sm:block" />
        {LAYERS.map((layer, i) => (
          <LayerRow key={layer.name} layer={layer} index={i} />
        ))}
      </div>

      {/* Infographic metrics */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4"
      >
        {METRICS.map((m) => (
          <motion.div key={m.label} variants={fadeUp} className="glass-card rounded-xl p-5">
            {m.render}
            <p className="mt-3 font-display text-2xl font-bold tracking-tight">{m.value}</p>
            <p className="text-sm font-medium">{m.label}</p>
            <p className="mt-1 text-xs text-muted-foreground">{m.note}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Tech stack */}
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mt-14"
      >
        <p className="text-center text-xs uppercase tracking-[0.2em] text-muted-foreground">
          Built with a modern, production-grade stack
        </p>
        <div className="mx-auto mt-6 max-w-5xl">
          <Marquee duration={28}>
            {STACK.map((tech) => (
              <span
                key={tech}
                className="flex items-center gap-2 whitespace-nowrap rounded-full border border-border/60 bg-background/50 px-4 py-1.5 font-mono text-xs text-muted-foreground"
              >
                <ShieldCheck className="h-3.5 w-3.5 text-chart-2" />
                {tech}
              </span>
            ))}
          </Marquee>
        </div>
      </motion.div>
    </section>
  )
}
