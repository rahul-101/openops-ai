import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type { LifecycleRecord, ReasoningReport } from "@/types/api"

export const reasoningKeys = {
  all: ["reasoning"] as const,
  history: () => [...reasoningKeys.all, "history"] as const,
  models: () => [...reasoningKeys.all, "models"] as const,
  lifecycle: () => [...reasoningKeys.all, "lifecycle"] as const,
  events: () => [...reasoningKeys.all, "events"] as const,
}

export interface ReasoningHistoryRecord {
  incident_id: string
  agents_involved: string[]
  decisions: string[]
  confidence: number
  risk: string
  outcome: string
  explanation?: Record<string, unknown>
}

export function useReasoningHistory(limit = 25) {
  return useQuery({
    queryKey: reasoningKeys.history(),
    queryFn: () => feClient.get<ReasoningHistoryRecord[]>(`/reasoning/history?limit=${limit}`),
    refetchInterval: 15_000,
  })
}

export function useLifecycleRecords() {
  return useQuery({
    queryKey: reasoningKeys.lifecycle(),
    queryFn: () => feClient.get<LifecycleRecord[]>("/aiops/lifecycle"),
    refetchInterval: 15_000,
  })
}

export interface IngestedEvent {
  event_id: string
  source: string
  title: string
  severity: string
  service: string | null
}

export function useIngestedEvents() {
  return useQuery({
    queryKey: reasoningKeys.events(),
    queryFn: () => feClient.get<IngestedEvent[]>("/aiops/events?limit=25"),
    refetchInterval: 10_000,
  })
}

export async function runReason(
  eventId: string,
): Promise<ReasoningReport> {
  return feClient.post<ReasoningReport>("/reasoning/reason", { event_id: eventId })
}

export async function runReasonOnIncident(
  eventId: string,
): Promise<ReasoningReport> {
  return feClient.post<ReasoningReport>("/reasoning/reason", { event_id: eventId })
}