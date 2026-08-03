import { useReducedMotion } from "framer-motion"
import { useEffect, useRef } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  r: number
  hue: number
}

export function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    if (reduceMotion) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches
    let raf = 0
    let particles: Particle[] = []
    let width = 0
    let height = 0

    const isDark = () => document.documentElement.classList.contains("dark")

    const resize = () => {
      const parent = canvas.parentElement
      if (!parent) return
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = parent.offsetWidth
      height = parent.offsetHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }

    const init = () => {
      const count = Math.min(Math.floor((width * height) / 18000), 70)
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.6 + 0.6,
        hue: Math.random() > 0.5 ? 243 : 263,
      }))
    }

    const draw = () => {
      ctx.clearRect(0, 0, width, height)
      const linkDist = 130

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]!
        p.x += p.vx
        p.y += p.vy

        if (p.x < -20) p.x = width + 20
        if (p.x > width + 20) p.x = -20
        if (p.y < -20) p.y = height + 20
        if (p.y > height + 20) p.y = -20

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = isDark()
          ? `hsla(${p.hue} 80% 72% / 0.55)`
          : `hsla(${p.hue} 60% 55% / 0.5)`
        ctx.fill()
      }

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i]!
          const b = particles[j]!
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.hypot(dx, dy)
          if (dist < linkDist) {
            const alpha = (1 - dist / linkDist) * 0.22
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.strokeStyle = isDark()
              ? `hsla(243 85% 70% / ${alpha})`
              : `hsla(243 60% 55% / ${alpha})`
            ctx.lineWidth = 0.6
            ctx.stroke()
          }
        }
      }

      raf = requestAnimationFrame(draw)
    }

    const onVisibility = () => {
      if (document.hidden) {
        cancelAnimationFrame(raf)
      } else if (!reduced) {
        raf = requestAnimationFrame(draw)
      }
    }

    resize()
    init()
    if (!reduced) raf = requestAnimationFrame(draw)

    window.addEventListener("resize", resize)
    document.addEventListener("visibilitychange", onVisibility)
    const mo = new ResizeObserver(resize)
    if (canvas.parentElement) mo.observe(canvas.parentElement)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener("resize", resize)
      document.removeEventListener("visibilitychange", onVisibility)
      mo.disconnect()
    }
  }, [reduceMotion])

  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-20 overflow-hidden">
      {/* Floating gradient orbs for depth */}
      <div className="absolute -top-32 left-1/4 h-[480px] w-[480px] rounded-full bg-primary/10 blur-[120px] motion-safe:animate-orb-a" />
      <div className="absolute right-[-120px] top-1/4 h-[420px] w-[420px] rounded-full bg-accent/10 blur-[120px] motion-safe:animate-orb-b" />
      <div className="absolute bottom-[-140px] left-[-100px] h-[460px] w-[460px] rounded-full bg-chart-3/10 blur-[140px] motion-safe:animate-orb-c" />
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  )
}
