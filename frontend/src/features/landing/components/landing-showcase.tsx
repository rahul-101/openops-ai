import { motion, useScroll, useTransform } from "framer-motion"
import { ArrowRight, Bot, CheckCircle2, ShieldCheck, TrendingUp, XCircle } from "lucide-react"
import { useRef } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { fadeUp, viewport } from "./motion"
import { cn } from "@/lib/utils"

function ParallaxVisual({ children, from = 40 }: { children: React.ReactNode; from?: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] })
  const y = useTransform(scrollYProgress, [0, 1], [from, -from])
  const rotate = useTransform(scrollYProgress, [0, 1], [2, -2])

  return (
    <motion.div ref={ref} style={{ y, rotate }} className="relative will-change-transform">
      {children}
    </motion.div>
  )
}

function TimelineMock() {
  return (
    <div className="glass-card rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-semibold">Incident #INC-2491</p>
        <Badge className="rounded-full bg-destructive/15 px-2 py-0.5 text-[10px] text-destructive">critical</Badge>
      </div>
      <div className="space-y-4">
        {[
          { time: "14:02:11", text: "Kubernetes alert · payments-api CrashLoopBackOff", icon: <Bot className="h-4 w-4 text-chart-1" />, tone: "text-chart-1" },
          { time: "14:02:14", text: "Agent correlated 6 events · 1.0 min before", icon: <Bot className="h-4 w-4 text-chart-2" />, tone: "text-chart-2" },
          { time: "14:02:31", text: "Root cause: bad image tag v2.1.3 on prod", icon: <CheckCircle2 className="h-4 w-4 text-success" />, tone: "text-success" },
          { time: "14:02:44", text: "Low-risk step executed · rolling back image", icon: <ShieldCheck className="h-4 w-4 text-chart-3" />, tone: "text-chart-3" },
        ].map((row, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -14 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.12, duration: 0.5 }}
            className="flex items-start gap-3"
          >
            <span className={cn("mt-0.5 flex h-7 w-7 items-center justify-center rounded-lg bg-background/50", row.tone)}>
              {row.icon}
            </span>
            <div>
              <p className="font-mono text-[10px] text-muted-foreground">{row.time}</p>
              <p className="text-sm">{row.text}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function ApprovalsMock() {
  return (
    <div className="glass-card rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-semibold">Awaiting approval</p>
        <Badge variant="outline" className="rounded-full px-2 py-0.5 text-[10px] text-warning">2 pending</Badge>
      </div>
      <div className="space-y-3">
        {[
          { action: "restart deployment · payments-api", risk: "medium", icon: <ShieldCheck className="h-4 w-4 text-warning" /> },
          { action: "rollback image · to v2.1.2", risk: "high", icon: <XCircle className="h-4 w-4 text-destructive" /> },
        ].map((a) => (
          <div key={a.action} className="flex items-center justify-between rounded-lg border border-border/60 bg-background/40 p-3">
            <div className="flex items-center gap-2.5">
              {a.icon}
              <p className="font-mono text-xs">{a.action}</p>
            </div>
            <div className="flex items-center gap-1.5">
              <Badge variant="outline" className={cn("rounded-full px-2 py-0.5 text-[10px]", a.risk === "high" ? "border-destructive/30 bg-destructive/10 text-destructive" : "border-warning/30 bg-warning/10 text-warning")}>
                {a.risk}
              </Badge>
              <span className="rounded-md bg-success/15 px-2 py-1 text-[10px] font-semibold text-success">Approve</span>
              <span className="rounded-md bg-destructive/15 px-2 py-1 text-[10px] font-semibold text-destructive">Reject</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ChartMock() {
  const bars = [42, 58, 47, 70, 63, 82, 74, 90, 78, 64, 72, 88]
  return (
    <div className="glass-card rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-semibold">MTTR over time</p>
        <div className="flex items-center gap-1.5 text-xs text-success">
          <TrendingUp className="h-4 w-4" /> -63%
        </div>
      </div>
      <div className="flex h-40 items-end gap-1.5">
        {bars.map((h, i) => (
          <motion.span
            key={i}
            initial={{ scaleY: 0 }}
            whileInView={{ scaleY: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay: i * 0.04 }}
            style={{ height: `${h}%` }}
            className="w-full origin-bottom rounded-sm bg-gradient-to-t from-chart-1 to-chart-2"
          />
        ))}
      </div>
    </div>
  )
}

const ROWS = [
  {
    eyebrow: "Command center",
    title: "One timeline for every incident",
    description: "Every alert, decision and action lands on a single scrolling timeline your whole team can follow in real time.",
    visual: <TimelineMock />,
  },
  {
    eyebrow: "Human in the loop",
    title: "Approve what matters, trust the rest",
    description: "Risk-gated approvals put engineers in control without slowing down the 95% of fixes that are safe to automate.",
    visual: <ApprovalsMock />,
    reverse: true,
  },
  {
    eyebrow: "Continuous improvement",
    title: "Watch metrics fall every week",
    description: "MTTR, alert fatigue and cost analytics show the impact of autonomous response — and where to tune runbooks.",
    visual: <ChartMock />,
  },
]

export function LandingShowcase() {
  return (
    <section id="security" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">Inside the platform</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-5xl">
          Built for operators,{" "}
          <span className="text-gradient">powered by agents</span>
        </h2>
      </div>

      <div className="mt-20 space-y-24">
        {ROWS.map((row) => (
          <motion.div
            key={row.title}
            variants={fadeUp}
            initial="hidden"
            whileInView="visible"
            viewport={viewport}
            className={cn("grid items-center gap-12 lg:grid-cols-2", row.reverse && "lg:[&>*:first-child]:order-2")}
          >
            <div className={cn(row.reverse && "lg:order-1")}>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-chart-2">{row.eyebrow}</p>
              <h3 className="mt-3 font-display text-2xl font-bold tracking-tight sm:text-3xl">{row.title}</h3>
              <p className="mt-4 max-w-lg text-muted-foreground">{row.description}</p>
            </div>
            <ParallaxVisual>{row.visual}</ParallaxVisual>
          </motion.div>
        ))}
      </div>

      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="mt-20 text-center"
      >
        <Button asChild size="lg" className="group h-12 px-7 text-base">
          <Link to="/auth/register">
            Explore the platform
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Button>
      </motion.div>
    </section>
  )
}
