import { useAuth } from "@/hooks/use-auth"

export function usePermission(permission: string) {
  const { user } = useAuth()
  
  if (!user) return false
  
  // Superusers have all permissions
  if (user.is_superuser) return true
  
  // Check if user has the specific permission based on role
  if (user.role === "admin") {
    return true // Admin has all permissions
  }
  
  // Regular user permissions
  if (user.role === "user") {
    return ["read", "write"].includes(permission)
  }
  
  // Default: no permissions
  return false
}

export function useRole(role: string) {
  const { user } = useAuth()
  
  if (!user) return false
  
  // Superusers have all roles
  if (user.is_superuser) return true
  
  // Check if user has the specific role
  return user.role === role
}