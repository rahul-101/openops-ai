import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type { AiActivitySnapshot, DashboardSnapshot, ExecutionsResponse, OperationsEvent } from "@/types/api"

export const dashboardKeys = {
  all: ["dashboard"] as const,
  snapshot: () => [...dashboardKeys.all, "snapshot"] as const,
  activity: () => [...dashboardKeys.all, "activity"] as const,
  events: () => [...dashboardKeys.all, "events"] as const,
  executions: () => [...dashboardKeys.all, "executions"] as const,
}

export function useDashboardSnapshot() {
  return useQuery({
    queryKey: dashboardKeys.snapshot(),
    queryFn: () => feClient.get<DashboardSnapshot>("/operations/dashboard"),
    refetchInterval: 15_000,
  })
}

export function useAiActivity() {
  return useQuery({
    queryKey: dashboardKeys.activity(),
    queryFn: () => feClient.get<AiActivitySnapshot>("/ai/activity"),
    refetchInterval: 10_000,
  })
}

export function useOperationsEvents(limit = 50) {
  return useQuery({
    queryKey: dashboardKeys.events(),
    queryFn: () => feClient.get<OperationsEvent[]>(`/operations/events?limit=${limit}`),
    refetchInterval: 10_000,
  })
}

export function useExecutions() {
  return useQuery({
    queryKey: dashboardKeys.executions(),
    queryFn: () => feClient.get<ExecutionsResponse>("/operations/executions"),
    refetchInterval: 10_000,
  })
}