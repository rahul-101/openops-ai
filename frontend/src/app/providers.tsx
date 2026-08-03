import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import * as React from "react"
import { Toaster } from "sonner"

import { ThemeProvider } from "@/components/theme-provider"
import { AppShellProvider } from "@/components/layout/app-shell-provider"

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 10_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="openops-theme">
        <AppShellProvider>
          {children}
          <Toaster richColors position="bottom-right" toastOptions={{ className: "!bg-card" }} />
        </AppShellProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}