import { ArrowLeft, Compass } from "lucide-react"
import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"

export function NotFoundPage() {
  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center px-6 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-chart-1 to-chart-2 text-white">
        <Compass className="h-8 w-8" />
      </div>
      <h1 className="mt-6 text-4xl font-bold tracking-tight">404</h1>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        This page doesn't exist or has been moved. Head back to the command center.
      </p>
      <Link to="/" className="mt-6">
        <Button>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to dashboard
        </Button>
      </Link>
    </div>
  )
}