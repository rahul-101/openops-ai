import * as React from "react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface CardShellProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  description?: string
  action?: React.ReactNode
  children: React.ReactNode
}

export function CardShell({
  title,
  description,
  action,
  children,
  className,
  ...props
}: CardShellProps) {
  return (
    <Card className={cn("relative flex flex-col overflow-hidden", className)} {...props}>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border/60 to-transparent"
      />
      {title && (
        <CardHeader className="flex-row items-start justify-between space-y-0">
          <div className="space-y-1">
            <CardTitle className="text-sm font-semibold">{title}</CardTitle>
            {description && <CardDescription className="text-xs">{description}</CardDescription>}
          </div>
          {action}
        </CardHeader>
      )}
      <CardContent className="flex-1">{children}</CardContent>
    </Card>
  )
}