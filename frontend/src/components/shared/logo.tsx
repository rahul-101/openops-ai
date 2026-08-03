import { cn } from "@/lib/utils"

export function LogoMark({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-chart-1 via-chart-2 to-chart-3 shadow-[0_2px_12px_hsl(var(--chart-2)/0.35)]",
        className,
      )}
    >
      <svg viewBox="0 0 24 24" width="17" height="17" fill="none" aria-hidden>
        <path
          d="M4 7.5h16M4 12h10M4 16.5h7"
          stroke="rgba(255,255,255,0.95)"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <circle cx="20" cy="16" r="2" fill="rgba(255,255,255,0.95)" />
      </svg>
    </div>
  )
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("flex items-center gap-2.5", className)}>
      <LogoMark />
      <span className="text-[15px] font-semibold tracking-tight">
        OpenOps<span className="bg-gradient-to-r from-chart-1 to-chart-2 bg-clip-text font-semibold text-transparent"> AI</span>
      </span>
    </span>
  )
}