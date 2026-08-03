import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type {
  AlertDecision,
  LifecycleRecord,
  OperationsEvent,
  Playbook,
} from "@/types/api"

export const operationsKeys = {
  all: ["operations"] as const,
  events: (limit: number) => [...operationsKeys.all, "events", limit] as const,
  executions: () => [...operationsKeys.all, "executions"] as const,
  activity: () => [...operationsKeys.all, "activity"] as const,
  dashboard: () => [...operationsKeys.all, "dashboard"] as const,
  playbooks: () => [...operationsKeys.all, "playbooks"] as const,
  riskActions: () => [...operationsKeys.all, "risk-actions"] as const,
  lifecycle: () => [...operationsKeys.all, "lifecycle"] as const,
}

export function useOperationsEvents(limit = 50) {
  return useQuery({
    queryKey: operationsKeys.events(limit),
    queryFn: () => feClient.get<OperationsEvent[]>(`/operations/events?limit=${limit}`),
    refetchInterval: 10_000,
  })
}

export function usePlaybooks() {
  return useQuery({
    queryKey: operationsKeys.playbooks(),
    queryFn: () => feClient.get<Playbook[]>("/aiops/playbooks"),
  })
}

export function useRiskActions() {
  return useQuery({
    queryKey: operationsKeys.riskActions(),
    queryFn: () => feClient.get<Record<string, string>>("/aiops/risk/actions"),
  })
}

export function useLifecycle() {
  return useQuery({
    queryKey: operationsKeys.lifecycle(),
    queryFn: () => feClient.get<LifecycleRecord[]>("/aiops/lifecycle"),
    refetchInterval: 15_000,
  })
}

export async function runLifecycle(payload: Record<string, unknown>): Promise<LifecycleRecord> {
  return feClient.post<LifecycleRecord>("/aiops/lifecycle/run", payload)
}

export async function ingestAlert(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return feClient.post<Record<string, unknown>>("/aiops/alerts/ingest", payload)
}

export async function decide(payload: Record<string, unknown>): Promise<AlertDecision> {
  return feClient.post<AlertDecision>("/aiops/decide", payload)
}