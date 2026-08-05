import * as React from "react"

interface AppShellState {
  mobileNavOpen: boolean
  setMobileNavOpen: (open: boolean) => void
}

const AppShellContext = React.createContext<AppShellState | null>(null)

export function AppShellProvider({ children }: { children: React.ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false)

  const value = React.useMemo<AppShellState>(
    () => ({ mobileNavOpen, setMobileNavOpen }),
    [mobileNavOpen],
  )

  return <AppShellContext.Provider value={value}>{children}</AppShellContext.Provider>
}

export function useAppShell() {
  const ctx = React.useContext(AppShellContext)
  if (!ctx) throw new Error("useAppShell must be used within AppShellProvider")
  return ctx
}
