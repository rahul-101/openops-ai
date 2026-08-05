import { motion } from "framer-motion"
import {
  BrainCircuit,
  Gauge,
  Lock,
  Network,
  ScrollText,
  Workflow,
  type LucideIcon,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { TiltCard } from "./tilt-card"
import { fadeUp, staggerContainer, viewport } from "./motion"

interface Feature {
  icon: LucideIcon
  title: string
  description: string
  accent: string
}

const FEATURES: Feature[] = [
  {
    icon: BrainCircuit,
    title: "Autonomous root-cause analysis",
    description: "AI agents correlate alerts, logs and deployment events to pinpoint the true cause of an incident in seconds.",
    accent: "from-chart-1/20 to-chart-1/5 text-chart-1",
  },
  {
    icon: Workflow,
    title: "Risk-gated remediation",
    description: "Every action is scored for risk. Low-risk fixes execute instantly; anything sensitive routes to human approval.",
    accent: "from-chart-2/20 to-chart-2/5 text-chart-2",
  },
  {
    icon: Network,
    title: "Multi-source ingestion",
    description: "Kubernetes, AWS, ServiceNow and 40+ integrations stream alerts into one normalized incident timeline.",
    accent: "from-chart-3/20 to-chart-3/5 text-chart-3",
  },
  {
    icon: ScrollText,
    title: "Living runbooks",
    description: "Playbooks auto-tune from past incidents, so your remediation steps improve after every event.",
    accent: "from-chart-4/20 to-chart-4/5 text-chart-4",
  },
  {
    icon: Gauge,
    title: "Model governance",
    description: "Route every AI call to the fastest, cheapest capable model with per-provider cost and latency telemetry.",
    accent: "from-chart-5/20 to-chart-5/5 text-chart-5",
  },
  {
    icon: Lock,
    title: "Audit-ready by default",
    description: "Every decision is recorded with approvals, user attribution and immutable audit trails for compliance.",
    accent: "from-chart-1/20 to-chart-1/5 text-chart-1",
  },
]

function FeatureCard({ feature }: { feature: Feature }) {
  const Icon = feature.icon

  return (
    <motion.div variants={fadeUp} className="h-full">
      <TiltCard
        className="h-full"
        innerClassName="group glass-card relative h-full rounded-xl p-6 shadow-[0_10px_40px_-20px_hsl(var(--chart-1)/0.25)] hover:shadow-[0_20px_60px_-20px_hsl(var(--chart-1)/0.4)] dark:shadow-[0_10px_40px_-20px_hsl(var(--chart-2)/0.3)] dark:hover:shadow-[0_20px_60px_-15px_hsl(var(--chart-2)/0.5)]"
      >
        <div
          aria-hidden
          className={cn(
            "pointer-events-none absolute inset-x-0 -top-20 h-40 bg-gradient-to-b to-transparent opacity-70 transition-opacity duration-500 group-hover:opacity-100",
            feature.accent.split(" ")[0],
          )}
        />
        <div className="relative">
          <div className={cn("inline-flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br transition-transform duration-300 group-hover:scale-110", feature.accent)}>
            <Icon className="h-5 w-5" />
          </div>
          <h3 className="mt-5 text-base font-semibold">{feature.title}</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{feature.description}</p>
        </div>
      </TiltCard>
    </motion.div>
  )
}

export function LandingFeatures() {
  return (
    <section id="features" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto max-w-2xl text-center"
      >
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">Features</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-5xl">
          Everything you need to{" "}
          <span className="text-gradient">close incidents faster</span>
        </h2>
        <p className="mt-4 text-muted-foreground">
          A full autonomous loop — from first alert to verified fix — with humans
          kept in the loop exactly where it matters.
        </p>
      </motion.div>

      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3"
      >
        {FEATURES.map((f) => (
          <FeatureCard key={f.title} feature={f} />
        ))}
      </motion.div>
    </section>
  )
}
