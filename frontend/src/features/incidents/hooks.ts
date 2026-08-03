import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type {
  CreateIncidentInput,
  Incident,
  IncidentSeverity,
  IncidentStatus,
  OperationsEvent,
  PaginatedResponse,
} from "@/types/api"

export const incidentKeys = {
  all: ["incidents"] as const,
  list: (params: IncidentListParams) => [...incidentKeys.all, "list", params] as const,
  detail: (id: string) => [...incidentKeys.all, "detail", id] as const,
  timeline: (id: string) => [...incidentKeys.all, "timeline", id] as const,
  workflow: (id: string) => [...incidentKeys.all, "workflow", id] as const,
}

export interface IncidentListParams {
  page?: number
  size?: number
  status?: IncidentStatus | null
  severity?: IncidentSeverity | null
  source?: string
  search?: string
}

export function useIncidents(params: IncidentListParams = {}) {
  const query = new URLSearchParams()
  if (params.page) query.set("page", String(params.page))
  if (params.size) query.set("size", String(params.size))
  if (params.status) query.set("status", params.status)
  if (params.severity) query.set("severity", params.severity)
  if (params.source) query.set("source", params.source)
  if (params.search) query.set("search", params.search)

  return useQuery({
    queryKey: incidentKeys.list(params),
    queryFn: () => feClient.get<PaginatedResponse<Incident>>(`/incidents?${query.toString()}`),
  })
}

export function useIncident(id: string | undefined) {
  return useQuery({
    queryKey: incidentKeys.detail(id ?? ""),
    queryFn: () => feClient.get<Incident>(`/incidents/${id}`),
    enabled: Boolean(id),
  })
}

export function useIncidentTimeline(id: string | undefined) {
  return useQuery({
    queryKey: incidentKeys.timeline(id ?? ""),
    queryFn: () => feClient.get<OperationsEvent[]>(`/incidents/${id}/timeline`),
    enabled: Boolean(id),
    refetchInterval: 10_000,
  })
}

export async function createIncident(input: CreateIncidentInput): Promise<Incident> {
  return feClient.post<Incident>("/incidents", input)
}

export async function updateIncident(id: string, input: CreateIncidentInput & { status: IncidentStatus }): Promise<Incident> {
  return feClient.put<Incident>(`/incidents/${id}`, input)
}

export async function deleteIncident(id: string): Promise<void> {
  return feClient.delete<void>(`/incidents/${id}`)
}