import { Outlet, useLocation } from "react-router-dom"
import { AnimatedBackground } from "@/components/shared/animated-background"
import { easeOutExpo } from "@/components/shared/motion"
import { motion } from "framer-motion"

export function AuthLayout() {
  const location = useLocation()
  
  return (
    <div className="relative flex min-h-screen bg-background">
      {/* Animated background for auth pages */}
      <AnimatedBackground />
      
      {/* Main content container */}
      <div className="relative flex w-full items-center justify-center p-4">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3, ease: easeOutExpo }}
          className="w-full max-w-md"
        >
          <Outlet />
        </motion.div>
      </div>
      
      {/* Optional branding */}
      <div className="absolute bottom-4 left-4 text-xs text-muted-foreground">
        OpenOps AI - Enterprise Incident Response Platform
      </div>
    </div>
  )
}