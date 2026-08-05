import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import { toast } from "sonner"

// Types from the auth service
export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  role: string
}

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  forgotPassword: (email: string) => Promise<void>
  getMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem("auth_token")
      if (token) {
        const response = await fetch("/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        
        if (response.ok) {
          const userData = await response.json()
          setUser(userData.data ?? null)
        } else {
          localStorage.removeItem("auth_token")
        }
      }
    } catch (error) {
      console.error("Auth check failed:", error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Login failed")
      }

      const data = await response.json()
      localStorage.setItem("auth_token", data.data.access_token)
      
      // Get user info
      await checkAuth()
      
      toast.success("Login successful")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed")
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: username, email, password, confirm_password: password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Registration failed")
      }

      const data = await response.json()
      localStorage.setItem("auth_token", data.data.access_token)
      
      // Get user info
      await checkAuth()
      
      toast.success("Registration successful! Please log in.")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Registration failed")
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const getMe = async () => {
    await checkAuth()
  }

  const logout = () => {
    localStorage.removeItem("auth_token")
    setUser(null)
    toast.info("Logged out")
  }

  const forgotPassword = async (email: string) => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Password recovery failed")
      }

      const data = await response.json()
      toast.success(data.message)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Password recovery failed")
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    forgotPassword,
    getMe,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}