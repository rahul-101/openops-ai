import { AnimatePresence, motion } from "framer-motion"
import { Outlet, useLocation } from "react-router-dom"

import { SidebarNav } from "@/components/layout/sidebar"
import { Topbar } from "@/components/layout/topbar"
import { useAppShell } from "@/components/layout/app-shell-provider"
import { Sheet, SheetContent } from "@/components/ui/sheet"
import { easeOutExpo } from "@/components/shared/motion"
import { AnimatedBackground } from "@/components/shared/animated-background"

export function AppShell() {
  const { mobileNavOpen, setMobileNavOpen } = useAppShell()
  const location = useLocation()

  return (
    <div className="relative flex min-h-screen bg-background">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r bg-sidebar/70 backdrop-blur-xl backdrop-saturate-150 lg:block">
        <SidebarNav />
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <SidebarNav />
        </SheetContent>
      </Sheet>

      <div className="flex min-w-0 flex-1 flex-col lg:pl-64">
        <Topbar />
        <main className="relative flex-1">
          <AnimatedBackground />
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 -z-10 grid-bg opacity-40"
          />
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25, ease: easeOutExpo }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}