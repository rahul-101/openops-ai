import { useAuth } from "@/hooks/use-auth"
import { ReactNode } from "react"
import { toast } from "sonner"

interface RoleGuardProps {
  children: ReactNode
  allowedRoles?: string[]
  requiredRole?: string
  requireAll?: boolean
  fallback?: ReactNode
}

export function RoleGuard({ 
  children, 
  allowedRoles = [],
  requiredRole,
  requireAll = false,
  fallback = null
}: RoleGuardProps) {
  const { user, isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return fallback
  }
  
  // Superusers can access any protected content
  if (user?.is_superuser) {
    return children
  }
  
  // Check role-based access
  const hasAccess = () => {
    if (requiredRole) {
      return user?.role === requiredRole
    }
    
    if (allowedRoles.length > 0) {
      if (requireAll) {
        return allowedRoles.every(role => user?.role === role)
      }
      return user?.role ? allowedRoles.includes(user.role) : false
    }
    
    return false
  }
  
  if (!hasAccess()) {
    if (fallback) {
      return fallback
    }
    
    toast.error("You don't have permission to access this content")
    return null
  }
  
  return children
}