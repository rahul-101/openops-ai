import * as React from "react"
import { CartesianGrid, ResponsiveContainer } from "recharts"

export const chartColors = {
  cyan: "hsl(var(--chart-1))",
  violet: "hsl(var(--chart-2))",
  magenta: "hsl(var(--chart-3))",
  green: "hsl(var(--chart-4))",
  amber: "hsl(var(--chart-5))",
}

export function ChartGrid() {
  return <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
}

interface TooltipEntry {
  name?: string | number
  value?: number | string
  color?: string
  fill?: string
}

export function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: TooltipEntry[]
  label?: string | number
}) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border bg-popover px-3 py-2 text-xs shadow-md">
      {label !== undefined && <p className="mb-1 font-medium text-popover-foreground">{label}</p>}
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 py-0.5">
          <span
            className="h-2.5 w-2.5 rounded-sm"
            style={{ backgroundColor: entry.color ?? entry.fill }}
          />
          <span className="capitalize text-muted-foreground">{entry.name}:</span>
          <span className="font-medium tabular-nums text-popover-foreground">
            {typeof entry.value === "number" ? entry.value.toLocaleString() : entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

export function ChartContainer({ children }: { children: React.ReactElement }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      {children}
    </ResponsiveContainer>
  )
}