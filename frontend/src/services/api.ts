import { client } from "@/lib/api"

const BASE = import.meta.env.VITE_API_URL ?? ""

/** Frontend client hitting the Vite dev proxy (`/api` → backend). */
export const feClient = {
  get: <T>(path: string) => client.get<T>(path, BASE),
  post: <T>(path: string, body?: unknown) => client.post<T>(path, body, BASE),
  put: <T>(path: string, body?: unknown) => client.put<T>(path, body, BASE),
  delete: <T>(path: string) => client.delete<T>(path, BASE),
}