/**
 * User service for managing users and RBAC operations.
 */

export async function getUsers() {
  const response = await fetch("/api/users")
  
  if (!response.ok) {
    throw new Error("Failed to fetch users")
  }
  
  const data = await response.json()
  return data
}

export async function updateUserRole(userId: string, role: string) {
  const response = await fetch(`/api/users/${userId}/role`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ role }),
  })
  
  if (!response.ok) {
    throw new Error("Failed to update user role")
  }
  
  return response.json()
}

export async function suspendUser(userId: string) {
  const response = await fetch(`/api/users/${userId}/suspend`, {
    method: "POST",
  })
  
  if (!response.ok) {
    throw new Error("Failed to suspend user")
  }
  
  return response.json()
}

export async function inviteUser(email: string, role: string, fullName?: string) {
  const response = await fetch("/api/users/invite", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, role, full_name: fullName }),
  })
  
  if (!response.ok) {
    throw new Error("Failed to invite user")
  }
  
  return response.json()
}