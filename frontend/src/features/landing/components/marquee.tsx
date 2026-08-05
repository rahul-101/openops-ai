import { cn } from "@/lib/utils"

interface MarqueeProps {
  children: React.ReactNode
  className?: string
  duration?: number
  mask?: boolean
}

export function Marquee({ children, className, duration = 36, mask = true }: MarqueeProps) {
  return (
    <div
      className={cn(
        "marquee-paused group/row relative flex w-full overflow-hidden",
        mask &&
          "[mask-image:linear-gradient(to_right,transparent,black_12%,black_88%,transparent)] [-webkit-mask-image:linear-gradient(to_right,transparent,black_12%,black_88%,transparent)]",
        className,
      )}
    >
      <div
        className="animate-marquee flex w-max items-center gap-x-14 shrink-0"
        style={{ "--marquee-duration": `${duration}s` } as React.CSSProperties}
      >
        {children}
        {children}
      </div>
    </div>
  )
}