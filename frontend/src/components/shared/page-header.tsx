import * as React from "react"

import { cn } from "@/lib/utils"

interface PageHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  description?: string
  eyebrow?: string
  action?: React.ReactNode
}

export function PageHeader({
  title,
  description,
  eyebrow,
  action,
  className,
  ...props
}: PageHeaderProps) {
  return (
    <div
      className={cn("flex flex-col gap-4 pb-6 sm:flex-row sm:items-end sm:justify-between", className)}
      {...props}
    >
      <div className="space-y-1.5">
        {eyebrow && (
          <p className="inline-flex w-fit items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-primary ring-1 ring-inset ring-primary/20">
            <span className="h-1.5 w-1.5 rounded-full bg-primary" aria-hidden />
            {eyebrow}
          </p>
        )}
        <h1 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">{title}</h1>
        {description && <p className="max-w-2xl text-sm text-muted-foreground">{description}</p>}
      </div>
      {action && <div className="flex shrink-0 items-center gap-2">{action}</div>}
    </div>
  )
}