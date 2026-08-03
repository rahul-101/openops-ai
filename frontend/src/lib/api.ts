export type ApiClientOptions = {
  baseUrl?: string
  headers?: Record<string, string>
  signal?: AbortSignal
}

const API_PREFIX = "/api"

async function request<T>(
  path: string,
  options: RequestInit = {},
  baseUrl?: string,
): Promise<T> {
  const url = `${baseUrl ?? ""}${API_PREFIX}${path}`
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 15_000)

  try {
    const res = await fetch(url, {
      ...options,
      signal: options.signal ?? controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!res.ok) {
      let message = `Request failed with status ${res.status}`
      try {
        const body = await res.json()
        if (typeof body.detail === "string") message = body.detail
        else if (body.detail) message = JSON.stringify(body.detail)
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, message, path)
    }

    if (res.status === 204) return undefined as T
    return (await res.json()) as T
  } finally {
    clearTimeout(timeoutId)
  }
}

export class ApiError extends Error {
  status: number
  path: string
  constructor(status: number, message: string, path: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.path = path
  }
}

export const client = {
  get<T>(path: string, base?: string): Promise<T> {
    return request<T>(path, { method: "GET" }, base)
  },
  post<T>(path: string, body?: unknown, base?: string): Promise<T> {
    return request<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }, base)
  },
  put<T>(path: string, body?: unknown, base?: string): Promise<T> {
    return request<T>(path, { method: "PUT", body: JSON.stringify(body ?? {}) }, base)
  },
  delete<T>(path: string, base?: string): Promise<T> {
    return request<T>(path, { method: "DELETE" }, base)
  },
}