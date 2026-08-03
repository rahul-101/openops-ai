import {
  Activity,
  BarChart3,
  BookOpen,
  Bot,
  Boxes,
  FileText,
  Gauge,
  Inbox,
  LayoutDashboard,
  ListChecks,
  MessageSquare,
  Plug,
  ScrollText,
  Server,
  Settings,
  User,
  Users,
  Workflow,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

export interface NavItem {
  title: string
  href: string
  icon: LucideIcon
  badge?: string | number
  match?: string
}

export interface NavGroup {
  label: string
  items: NavItem[]
}

export const navigationGroups: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { title: "Dashboard", href: "/", icon: LayoutDashboard, match: "/" },
      { title: "Operation Overview", href: "/overview", icon: Activity },
      { title: "AI Command Center", href: "/command-center", icon: Bot },
      { title: "AI Chat", href: "/chat", icon: MessageSquare },
    ],
  },
  {
    label: "Automation",
    items: [
      { title: "Agents", href: "/agents", icon: Bot },
      { title: "Workflows", href: "/workflows", icon: Workflow },
      { title: "Pipelines", href: "/pipelines", icon: Boxes },
      { title: "Alerts", href: "/alerts", icon: Inbox },
      { title: "Tasks", href: "/tasks", icon: ListChecks },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { title: "Analytics", href: "/analytics", icon: BarChart3 },
      { title: "Reports", href: "/reports", icon: FileText },
      { title: "Logs", href: "/logs", icon: ScrollText },
      { title: "Knowledge Base", href: "/knowledge", icon: BookOpen },
    ],
  },
  {
    label: "Platform",
    items: [
      { title: "Models", href: "/models", icon: Gauge, match: "/models" },
      { title: "Integrations", href: "/integrations", icon: Plug },
      { title: "System Health", href: "/health", icon: Server },
      { title: "Users & Roles", href: "/users", icon: Users },
    ],
  },
]

export const sectionNav: NavItem[] = [
  { title: "Profile", href: "/profile", icon: User },
  { title: "Settings", href: "/settings", icon: Settings },
]