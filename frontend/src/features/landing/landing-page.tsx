import { motion, useScroll, useSpring } from "framer-motion"

import { LandingNavbar } from "./components/landing-navbar"
import { LandingBackground } from "./components/landing-background"
import { LandingHero } from "./components/landing-hero"
import { LandingFeatures } from "./components/landing-features"
import { LandingStats } from "./components/landing-stats"
import { LandingHowItWorks } from "./components/landing-how-it-works"
import { LandingShowcase } from "./components/landing-showcase"
import { LandingInfographics } from "./components/landing-infographics"
import { LandingFlow } from "./components/landing-flow"
import { LandingCta } from "./components/landing-cta"
import { LandingFooter } from "./components/landing-footer"

export function LandingPage() {
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, { stiffness: 90, damping: 28, restDelta: 0.001 })

  return (
    <div className="relative min-h-screen overflow-x-clip text-foreground">
      <motion.div
        style={{ scaleX }}
        className="fixed inset-x-0 top-0 z-[60] h-0.5 origin-left bg-gradient-to-r from-chart-1 via-chart-2 to-chart-3"
      />
      <LandingBackground />
      <LandingNavbar />
      <main>
        <LandingHero />
        <LandingStats />
        <LandingFeatures />
        <LandingHowItWorks />
        <LandingShowcase />
        <LandingInfographics />
        <LandingFlow />
        <LandingCta />
      </main>
      <LandingFooter />
    </div>
  )
}
