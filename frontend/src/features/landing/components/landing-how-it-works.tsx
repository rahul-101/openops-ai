import { motion } from "framer-motion"
import { Radar, ScanSearch, Wrench } from "lucide-react"
import type { LucideIcon } from "lucide-react"

import { fadeUp, staggerContainer, viewport } from "./motion"
import { cn } from "@/lib/utils"

interface Step {
  icon: LucideIcon
  step: string
  title: string
  description: string
}

const STEPS: Step[] = [
  {
    icon: Radar,
    step: "01",
    title: "Detect & correlate",
    description: "Alerts from Kubernetes, AWS and ticketing systems are normalized and correlated into a single incident timeline.",
  },
  {
    icon: ScanSearch,
    step: "02",
    title: "Diagnose",
    description: "Agents pull logs, metrics and deployment history to build a root-cause analysis with confidence scoring.",
  },
  {
    icon: Wrench,
    step: "03",
    title: "Remediate",
    description: "The planner drafts a runbook. Low-risk steps run automatically; high-risk steps wait for one-click approval.",
  },
]

export function LandingHowItWorks() {
  return (
    <section id="how-it-works" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mx-auto max-w-2xl text-center"
      >
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">How it works</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-5xl">
          From alert to resolution in{" "}
          <span className="text-gradient">three steps</span>
        </h2>
      </motion.div>

      <div className="relative mt-16">
        <div aria-hidden className="absolute left-0 right-0 top-7 hidden h-px lg:block">
          <svg className="h-full w-full" preserveAspectRatio="none" viewBox="0 0 1200 2">
            <line x1="0" y1="1" x2="1200" y2="1" stroke="hsl(var(--chart-2)/0.35)" strokeWidth="2" strokeDasharray="8 8" />
          </svg>
        </div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewport}
          className="grid gap-10 lg:grid-cols-3"
        >
          {STEPS.map((s) => (
            <motion.div key={s.step} variants={fadeUp} className="relative flex flex-col items-center text-center">
              <div className="relative z-10 flex h-14 w-14 items-center justify-center rounded-2xl border border-chart-2/30 bg-gradient-to-br from-chart-1/20 to-chart-2/20 text-chart-2 shadow-[0_10px_30px_-10px_hsl(var(--chart-1)/0.5)]">
                <s.icon className="h-6 w-6" />
              </div>
              <p className={cn("mt-5 font-mono text-xs font-medium tracking-widest text-muted-foreground")}>STEP {s.step}</p>
              <h3 className="mt-2 text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 max-w-xs text-sm leading-relaxed text-muted-foreground">{s.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
