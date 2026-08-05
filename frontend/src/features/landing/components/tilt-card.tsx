import { useRef } from "react"

import { cn } from "@/lib/utils"

interface TiltCardProps {
  children: React.ReactNode
  className?: string
  innerClassName?: string
  max?: number
  glare?: boolean
  scale?: number
}

export function TiltCard({
  children,
  className,
  innerClassName,
  max = 9,
  glare = true,
  scale = 1.02,
}: TiltCardProps) {
  const outerRef = useRef<HTMLDivElement>(null)
  const innerRef = useRef<HTMLDivElement>(null)
  const glareRef = useRef<HTMLDivElement>(null)

  const handleMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const outer = outerRef.current
    const inner = innerRef.current
    const gl = glareRef.current
    if (!outer || !inner) return

    const rect = outer.getBoundingClientRect()
    const px = (e.clientX - rect.left) / rect.width
    const py = (e.clientY - rect.top) / rect.height
    const rx = (0.5 - py) * max
    const ry = (px - 0.5) * max

    inner.style.transform = `perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) scale3d(${scale},${scale},${scale})`

    if (gl && glare) {
      gl.style.background = `radial-gradient(circle at ${px * 100}% ${py * 100}%, hsl(var(--card) / 0.16), transparent 55%)`
      gl.style.opacity = "1"
    }
  }

  const handleLeave = () => {
    const inner = innerRef.current
    const gl = glareRef.current
    if (inner) inner.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)"
    if (gl) gl.style.opacity = "0"
  }

  return (
    <div
      ref={outerRef}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      className={cn("[perspective:1200px]", className)}
    >
      <div
        ref={innerRef}
        className={cn(
          "relative overflow-hidden shadow-sm transition-transform duration-300 ease-out will-change-transform",
          innerClassName,
        )}
      >
        {children}

        {glare && (
          <div
            ref={glareRef}
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300"
          />
        )}

        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-foreground/15 to-transparent"
        />
      </div>
    </div>
  )
}