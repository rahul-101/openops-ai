import * as React from "react"
import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type { ProviderHealth } from "@/types/api"

interface AppShellState {
  mobileNavOpen: boolean
  setMobileNavOpen: (open: boolean) => void
  environment: string
  providers: ProviderHealth[]
  loading: boolean
}

const AppShellContext = React.createContext<AppShellState | null>(null)

export function AppShellProvider({ children }: { children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false)

  const health = useQuery({
    queryKey: ["provider-health", "shell"],
    queryFn: () => feClient.get<ProviderHealth[]>("/ai/providers/health"),
    refetchInterval: 30_000,
    staleTime: 15_000,
  })

  const value = React.useMemo<AppShellState>(
    () => ({
      mobileNavOpen,
      setMobileNavOpen,
      environment: import.meta.env.VITE_ENVIRONMENT ?? "development",
      providers: health.data ?? [],
      loading: health.isLoading,
    }),
    [mobileNavOpen, health.data, health.isLoading],
  )

  return <AppShellContext.Provider value={value}>{children}</AppShellContext.Provider>
}

export function useAppShell() {
  const ctx = React.useContext(AppShellContext)
  if (!ctx) throw new Error("useAppShell must be used within AppShellProvider")
  return ctx
}