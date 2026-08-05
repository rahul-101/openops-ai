import { BrowserRouter, Route, Routes } from "react-router-dom"

import { AppShell } from "@/layouts/app-shell"
import { AuthLayout } from "@/features/auth/auth-layout"
import { LandingPage } from "@/features/landing/landing-page"
import { LoginPage, RegisterPage, ForgotPasswordPage } from "@/features/auth/pages"
import { DashboardPage } from "@/features/dashboard/dashboard-page"
import { AiCommandCenterPage } from "@/features/command-center/command-center-page"
import { AiChatPage } from "@/features/chat/chat-page"
import { ModelGovernancePage } from "@/features/governance/model-governance-page"
import { PlaybooksPage } from "@/features/playbooks/playbooks-page"

import { OverviewPage } from "@/features/operations/overview-page"
import { AgentsPage } from "@/features/agents/agents-page"
import { WorkflowsPage } from "@/features/workflows/workflows-page"
import { AlertsPage } from "@/features/alerts/alerts-page"
import { SetupPage } from "@/features/setup/setup-page"
import { AnalyticsPage } from "@/features/analytics/analytics-page"
import { IncidentsPage } from "@/features/incidents/incidents-page"
import { IncidentDetailPage } from "@/features/incidents/incident-detail-page"
import { ReportsPage } from "@/features/reports/reports-page"
import { LogsPage } from "@/features/operations/logs-page"
import { KnowledgePage } from "@/features/knowledge/knowledge-page"
import { ModelsPage } from "@/features/models/models-page"
import { IntegrationsPage } from "@/features/integrations/integrations-page"
import { SystemHealthPage } from "@/features/health/system-health-page"
import { UsersPage } from "@/features/users/users-page"
import { ApprovalsPage } from "@/features/approvals/approvals-page"
import { SettingsPage } from "@/features/settings/settings-page"
import { NotFoundPage } from "@/features/misc/not-found-page"

import { ProfilePage } from "@/features/settings/profile-page"

import { ProtectedRoute } from "@/components/auth/protected-route"
import { PublicRoute } from "@/components/auth/protected-route"
import { RoleGuard } from "@/components/auth/role-guard"


const ProtectedAppShell = () => (
  <ProtectedRoute>
    <AppShell />
  </ProtectedRoute>
)

const UsersPageWrapper = () => (
  <RoleGuard allowedRoles={["admin", "operator"]}>
    <UsersPage />
  </RoleGuard>
)


export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          element={
            <PublicRoute>
              <AuthLayout />
            </PublicRoute>
          }
        >
          <Route path="/auth" element={<LoginPage />} />
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
        </Route>
        <Route element={<ProtectedAppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="command-center" element={<AiCommandCenterPage />} />
          <Route path="chat" element={<AiChatPage />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="workflows" element={<WorkflowsPage />} />
          <Route path="pipelines" element={<SetupPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="tasks" element={<IncidentsPage />} />
          <Route path="approvals" element={<ApprovalsPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="incidents/:id" element={<IncidentDetailPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="logs" element={<LogsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="integrations" element={<IntegrationsPage />} />
          <Route path="health" element={<SystemHealthPage />} />
          <Route path="users" element={<UsersPageWrapper />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="governance" element={<ModelGovernancePage />} />
          <Route path="playbooks" element={<PlaybooksPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}