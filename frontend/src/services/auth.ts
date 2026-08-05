import { QueryClient } from "@tanstack/react-query"

export async function loginUser(email: string, password: string) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: email, password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Login failed")
  }

  const data = await response.json()
  return data
}

export async function registerUser(name: string, email: string, password: string) {
  const response = await fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, email, password, confirm_password: password }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Registration failed")
  }

  const data = await response.json()
  return data
}

export async function getCurrentUser() {
  const response = await fetch("/api/auth/me", {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
    },
  })

  if (!response.ok) {
    throw new Error("Failed to get user")
  }

  const data = await response.json()
  return data
}

export function setupAuthQueries(queryClient: QueryClient) {
  return {
    loginUser: {
      mutationFn: ({ email, password }: { email: string; password: string }) =>
        loginUser(email, password),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["user"] })
      },
    },
    registerUser: {
      mutationFn: ({ name, email, password }: { name: string; email: string; password: string }) =>
        registerUser(name, email, password),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["user"] })
      },
    },
    getCurrentUser: {
      queryKey: ["user"],
      queryFn: getCurrentUser,
    },
  }
}