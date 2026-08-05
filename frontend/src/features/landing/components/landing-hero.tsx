import { motion, useScroll, useTransform } from "framer-motion"
import { ArrowRight, Play, ShieldCheck, Sparkles, Zap } from "lucide-react"
import { useRef } from "react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useAuth } from "@/hooks/use-auth"
import { HeroVisual } from "./hero-visual"
import { EASE } from "./motion"

const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12, delayChildren: 0.15 } },
}

const item = {
  hidden: { opacity: 0, y: 26 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: EASE } },
}

const HERO_BARS = [38, 52, 44, 62, 56, 72, 64, 84, 76, 92, 68, 80]

export function LandingHero() {
  const { isAuthenticated } = useAuth()
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] })
  const sceneY = useTransform(scrollYProgress, [0, 1], [0, 120])
  const sceneOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0.15])

  return (
    <section id="top" ref={ref} className="relative min-h-screen overflow-hidden">
      {/* Ambient background */}
      <div className="pointer-events-none absolute inset-0 -z-20">
        <div className="absolute -top-32 left-1/4 h-[560px] w-[560px] rounded-full bg-primary/15 blur-[140px] motion-safe:animate-orb-a" />
        <div className="absolute right-[-120px] top-1/3 h-[480px] w-[480px] rounded-full bg-accent/15 blur-[140px] motion-safe:animate-orb-b" />
        <div className="absolute bottom-[-160px] left-[10%] h-[420px] w-[420px] rounded-full bg-chart-3/10 blur-[140px] motion-safe:animate-orb-c" />
        <div className="grid-bg absolute inset-0 opacity-60" />
      </div>

      {/* Floating app panels */}
      <motion.div
        style={{ y: sceneY, opacity: sceneOpacity }}
        className="pointer-events-none absolute inset-0 -z-10"
        aria-hidden
      >
        <HeroVisual />
      </motion.div>

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-5 pb-24 pt-32 text-center sm:px-8">
        <motion.div variants={container} initial="hidden" animate="visible" className="flex w-full max-w-4xl flex-col items-center">
          <motion.div variants={item}>
            <Badge
              variant="outline"
              className="glass-card gap-2 rounded-full px-4 py-1.5 text-xs font-medium text-muted-foreground"
            >
              <Sparkles className="h-3.5 w-3.5 text-chart-2" />
              Autonomous AI incident response for modern platforms
            </Badge>
          </motion.div>

          <motion.h1
            variants={item}
            className="mt-6 font-display text-4xl font-bold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl"
          >
            Detect, diagnose and fix
            <span className="text-gradient"> incidents autonomously</span>
          </motion.h1>

          <motion.p
            variants={item}
            className="mt-6 max-w-2xl text-base text-muted-foreground sm:text-lg"
          >
            OpenOps AI correlates alerts, runs root-cause analysis and executes
            risk-gated remediations in minutes — while your engineers sleep.
          </motion.p>

          <motion.div variants={item} className="mt-9 flex flex-col items-center gap-3 sm:flex-row">
            {isAuthenticated ? (
              <Button asChild size="lg" className="group h-12 px-7 text-base">
                <Link to="/dashboard">
                  Open dashboard
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            ) : (
              <Button asChild size="lg" className="group h-12 px-7 text-base">
                <Link to="/auth/register">
                  Start free
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            )}
            <Button asChild size="lg" variant="outline" className="h-12 px-7 text-base">
              <a href="#how-it-works">
                <Play className="h-4 w-4" />
                See how it works
              </a>
            </Button>
          </motion.div>

          <motion.div variants={item} className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
            {[
              { icon: ShieldCheck, label: "SOC 2 aligned" },
              { icon: Zap, label: "Sub-minute response" },
              { icon: Sparkles, label: "3 AI agents working for you" },
            ].map(({ icon: Icon, label }) => (
              <span key={label} className="inline-flex items-center gap-1.5">
                <Icon className="h-3.5 w-3.5 text-chart-1" />
                {label}
              </span>
            ))}
          </motion.div>
        </motion.div>
      </div>

      {/* Floating dashboard mockup */}
      <motion.div
        initial={{ opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: EASE, delay: 0.9 }}
        className="relative z-10 mx-auto -mt-24 max-w-4xl px-5 sm:px-8"
      >
        <div className="glass-card rounded-2xl p-4 shadow-[0_30px_80px_-20px_hsl(var(--chart-1)/0.35)] dark:shadow-[0_30px_80px_-20px_hsl(var(--chart-2)/0.4)]">
          <div className="flex items-center justify-between border-b border-border/70 pb-3">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-destructive/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/80" />
            </div>
            <p className="font-mono text-xs text-muted-foreground">incident · payments-api-crash</p>
            <Badge variant="outline" className="rounded-full bg-success/10 px-2 py-0.5 text-[10px] text-success">
              Auto-resolved in 42s
            </Badge>
          </div>
          <div className="grid gap-4 p-4 sm:grid-cols-[1fr_auto]">
            <div className="space-y-3">
              {[
                { label: "Root cause", value: "Pod CrashLoopBackOff", tone: "text-chart-3" },
                { label: "Action", value: "Restarted deployment · rolled back image", tone: "text-chart-2" },
                { label: "Risk", value: "Low · executed automatically", tone: "text-success" },
              ].map((row) => (
                <div key={row.label} className="flex flex-col gap-0.5 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
                  <span className="text-xs text-muted-foreground">{row.label}</span>
                  <span className={`text-sm font-medium ${row.tone}`}>{row.value}</span>
                </div>
              ))}
            </div>
            <div className="flex h-24 items-end gap-1.5 rounded-lg border border-border/60 bg-background/40 p-3">
              {HERO_BARS.map((h, i) => (
                <motion.span
                  key={i}
                  initial={{ scaleY: 0 }}
                  animate={{ scaleY: 1 }}
                  transition={{ duration: 0.7, ease: EASE, delay: 1.1 + i * 0.03 }}
                  style={{ height: `${h}%` }}
                  className="w-2 origin-bottom rounded-sm bg-gradient-to-t from-chart-1 to-chart-2"
                />
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      <div className="pointer-events-none absolute bottom-6 left-1/2 z-10 -translate-x-1/2">
        <div className="flex h-9 w-6 items-start justify-center rounded-full border border-muted-foreground/40 p-1.5">
          <motion.span
            animate={{ y: [0, 12, 0], opacity: [1, 0.2, 1] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
            className="h-2 w-1 rounded-full bg-chart-2"
          />
        </div>
      </div>
    </section>
  )
}
