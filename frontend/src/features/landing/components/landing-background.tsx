import { useEffect, useRef } from "react"

import { useTheme } from "@/components/theme-provider"

interface Node {
  x: number
  y: number
  r: number
  layer: number
  baseGlow: number
}

interface Edge {
  a: number
  b: number
  speed: number
  phase: number
}

function hslToRgba(color: string, alpha: number) {
  const m = color.trim().match(/^([\d.]+)\s+([\d.]+)%\s+([\d.]+)%$/)
  if (!m) return `hsla(256, 92%, 66%, ${alpha})`
  return `hsla(${m[1]}, ${m[2]}%, ${m[3]}%, ${alpha})`
}

function readCssVar(name: string, fallback: string) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v ? v : fallback
}

function usePrefersReducedMotion() {
  const ref = useRef(false)
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)")
    ref.current = mq.matches
    const onChange = (e: MediaQueryListEvent) => (ref.current = e.matches)
    mq.addEventListener("change", onChange)
    return () => mq.removeEventListener("change", onChange)
  }, [])
  return ref
}

export function LandingBackground() {
  const { theme } = useTheme()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const reducedRef = usePrefersReducedMotion()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let raf = 0
    let width = 0
    let height = 0
    let nodes: Node[] = []
    let edges: Edge[] = []
    let colors = { p: "#8b5cf6", s: "#06b6d4", dot: "#8b5cf6" }
    const dpr = Math.min(window.devicePixelRatio || 1, 2)

    const generate = () => {
      const cols = 7
      const rows = 8
      const cellW = width / (cols + 1)
      const cellH = height / (rows + 1)
      nodes = []
      edges = []
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          if (Math.random() < 0.18) continue
          nodes.push({
            x: cellW * (c + 1) + (Math.random() - 0.5) * cellW * 0.7,
            y: cellH * (r + 1) + (Math.random() - 0.5) * cellH * 0.7,
            r: 1.2 + Math.random() * 1.8,
            layer: Math.floor(r / 2),
            baseGlow: 0.3 + Math.random() * 0.3,
          })
        }
      }
      const phases = nodes.map(() => Math.random() * Math.PI * 2)
      for (let i = 0; i < nodes.length; i++) {
        const ni = nodes[i]
        if (!ni) continue
        const nearest = nodes
          .map((n, j) => ({ j, d: Math.hypot(n.x - ni.x, n.y - ni.y) }))
          .filter((x) => x.j !== i)
          .sort((a, b) => a.d - b.d)
          .slice(0, 2)
          .map((x) => x.j)

        for (const j of nearest) {
          if (edges.some((e) => (e.a === i && e.b === j) || (e.a === j && e.b === i))) continue
          edges.push({ a: i, b: j, speed: 0.0006 + Math.random() * 0.0009, phase: phases[i] ?? 0 })
        }
      }
    }

    const resize = () => {
      const parent = canvas.parentElement
      width = parent?.clientWidth ?? window.innerWidth
      height = window.innerHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      generate()
    }

    const draw = (t: number) => {
      const reduced = reducedRef.current
      ctx.clearRect(0, 0, width, height)

      // edges
      for (const e of edges) {
        const a = nodes[e.a]
        const b = nodes[e.b]
        if (!a || !b) continue
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.strokeStyle = hslToRgba(colors.s, 0.10)
        ctx.lineWidth = 1
        ctx.stroke()

        // travelling pulse
        const prog = reduced ? 0.5 : (t * e.speed + e.phase) % 1
        const px = a.x + (b.x - a.x) * prog
        const py = a.y + (b.y - a.y) * prog
        const grad = ctx.createRadialGradient(px, py, 0, px, py, 6)
        grad.addColorStop(0, hslToRgba(colors.p, 0.5))
        grad.addColorStop(1, hslToRgba(colors.p, 0))
        ctx.beginPath()
        ctx.arc(px, py, 6, 0, Math.PI * 2)
        ctx.fillStyle = grad
        ctx.fill()
      }

      // nodes
      for (const n of nodes) {
        const glow = n.baseGlow + (reduced ? 0 : Math.sin(t * 0.001 + n.x * 0.002) * 0.15)
        const radius = reduced ? n.r : n.r + Math.sin(t * 0.0016 + n.layer) * 0.4
        const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, radius * 6)
        grad.addColorStop(0, hslToRgba(n.layer % 2 === 0 ? colors.p : colors.s, 0.35 + 0.3 * glow))
        grad.addColorStop(1, hslToRgba(n.layer % 2 === 0 ? colors.p : colors.s, 0))
        ctx.beginPath()
        ctx.arc(n.x, n.y, radius * 6, 0, Math.PI * 2)
        ctx.fillStyle = grad
        ctx.fill()

        ctx.beginPath()
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2)
        ctx.fillStyle = hslToRgba(n.layer % 2 === 0 ? colors.p : colors.s, 0.9)
        ctx.fill()
      }

      if (!reduced) raf = requestAnimationFrame(draw)
    }

    const applyColors = () => {
      const c1 = readCssVar("--chart-1", "#8b5cf6")
      const c2 = readCssVar("--chart-2", "#06b6d4")
      colors = { p: c1, s: c2, dot: c1 }
    }

    applyColors()
    resize()
    const observer = new ResizeObserver(() => {
      applyColors()
      resize()
    })
    observer.observe(canvas)

    const isReduced = reducedRef.current
    if (!isReduced) raf = requestAnimationFrame(draw)

    const onVisibility = () => {
      cancelAnimationFrame(raf)
      if (document.visibilityState === "visible") {
        applyColors()
        resize()
        if (!reducedRef.current) raf = requestAnimationFrame(draw)
      }
    }
    document.addEventListener("visibilitychange", onVisibility)

    return () => {
      cancelAnimationFrame(raf)
      observer.disconnect()
      document.removeEventListener("visibilitychange", onVisibility)
    }
  }, [theme])

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/40 to-background" />
      <canvas ref={canvasRef} className="absolute inset-0 opacity-70" />
    </div>
  )
}