import { useQuery } from "@tanstack/react-query"

import { feClient } from "@/services/api"
import type { AgentAnalytics } from "@/types/api"

export const agentsKeys = {
  all: ["agents"] as const,
  analytics: () => [...agentsKeys.all, "analytics"] as const,
  summary: () => [...agentsKeys.all, "summary"] as const,
}

export interface AgentSummary {
  total_agents: number
  total_runs: number
  overall_success_rate: number
}

export function useAgentAnalytics() {
  return useQuery({
    queryKey: agentsKeys.analytics(),
    queryFn: () => feClient.get<AgentAnalytics[]>("/optimization/agents"),
    refetchInterval: 15_000,
  })
}

export function useAgentSummary() {
  return useQuery({
    queryKey: agentsKeys.summary(),
    queryFn: () => feClient.get<AgentSummary>("/optimization/agents/summary"),
    refetchInterval: 15_000,
  })
}