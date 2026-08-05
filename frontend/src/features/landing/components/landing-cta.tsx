import { motion } from "framer-motion"
import { ArrowRight, Sparkles } from "lucide-react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { fadeUp, viewport } from "./motion"

export function LandingCta() {
  return (
    <section className="relative mx-auto max-w-7xl px-5 pb-24 pt-8 sm:px-8 sm:pb-32">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={viewport}
        className="relative overflow-hidden rounded-3xl border border-chart-2/30 bg-gradient-to-br from-chart-1/15 via-background/40 to-chart-2/15 px-6 py-20 text-center sm:px-12"
      >
        <div aria-hidden className="pointer-events-none absolute -top-24 left-1/2 h-64 w-[520px] -translate-x-1/2 rounded-full bg-chart-2/20 blur-[120px]" />
        <div className="relative">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-chart-1 to-chart-2 shadow-lg">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <h2 className="mx-auto mt-6 max-w-2xl font-display text-3xl font-bold tracking-tight sm:text-5xl">
            Sleep through your next incident
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
            Join teams that cut MTTR by 10x. Set up OpenOps AI in under 30 minutes and watch your first incident resolve itself.
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button asChild size="lg" className="group h-12 px-7 text-base">
              <Link to="/auth/register">
                Get started free
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="h-12 px-7 text-base">
              <Link to="/auth">Sign in</Link>
            </Button>
          </div>
        </div>
      </motion.div>
    </section>
  )
}
