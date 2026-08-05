import { animate, motion, useInView, useMotionValue, useTransform } from "framer-motion"
import { useEffect, useRef } from "react"

import { fadeUp, staggerContainer, viewport } from "./motion"

interface Stat {
  value: number
  suffix: string
  label: string
  decimals?: number
}

const STATS: Stat[] = [
  { value: 99.99, suffix: "%", label: "Alert triage accuracy", decimals: 2 },
  { value: 42, suffix: "s", label: "Median time to resolution" },
  { value: 180, suffix: "k+", label: "Incidents handled autonomously" },
  { value: 40, suffix: "+", label: "Native integrations" },
]

function CountUp({ value, suffix, decimals = 0 }: { value: number; suffix: string; decimals?: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: "-60px" })
  const mv = useMotionValue(0)
  const display = useTransform(mv, (v) => `${v.toFixed(decimals)}${suffix}`)

  useEffect(() => {
    if (!inView) return
    const controls = animate(mv, value, { duration: 1.8, ease: [0.16, 1, 0.3, 1] })
    return controls.stop
  }, [inView, mv, value])

  return (
    <motion.span ref={ref} className="font-display text-4xl font-bold tracking-tight sm:text-5xl">
      <motion.span>{display}</motion.span>
    </motion.span>
  )
}

export function LandingStats() {
  return (
    <section className="relative mx-auto max-w-7xl px-5 sm:px-8">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="glass-card grid grid-cols-2 gap-px overflow-hidden rounded-2xl lg:grid-cols-4"
      >
        {STATS.map((stat) => (
          <motion.div key={stat.label} variants={fadeUp} className="flex flex-col items-center gap-2 bg-background/40 px-6 py-12 text-center">
            <CountUp value={stat.value} suffix={stat.suffix} decimals={stat.decimals} />
            <p className="max-w-[180px] text-sm text-muted-foreground">{stat.label}</p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  )
}
