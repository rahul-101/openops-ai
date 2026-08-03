import { NavLink, useLocation } from "react-router-dom"

import { Logo } from "@/components/shared/logo"
import { cn } from "@/lib/utils"
import { navigationGroups, sectionNav } from "@/config/navigation"
import { ScrollArea } from "@/components/ui/scroll-area"

function isActive(href: string, pathname: string): boolean {
  if (href === "/") return pathname === "/"
  return pathname === href || pathname.startsWith(href + "/")
}

export function SidebarNav() {
  const { pathname } = useLocation()

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 shrink-0 items-center border-b px-5">
        <Logo />
      </div>      <ScrollArea className="flex-1 px-3 py-3">
        <nav className="space-y-5" aria-label="Primary">
          {navigationGroups.map((group) => (
            <div key={group.label} className="space-y-1">
              <p className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {group.label}
              </p>
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const active = isActive(item.href, pathname)
                  return (
                    <li key={item.title}>
                      <NavItemLink item={item} active={active} />
                    </li>
                  )
                })}
              </ul>
            </div>
          ))}
        </nav>

        <div className="mt-6 border-t pt-4">
          <div className="space-y-0.5">
            {sectionNav.map((item) => {
              const active = isActive(item.href, pathname)
              return <NavItemLink key={item.title} item={item} active={active} />
            })}
          </div>
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="flex items-center gap-3 rounded-lg border bg-card/60 p-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-chart-1 to-chart-2 text-[11px] font-semibold text-white">
            ab
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">Ops Admin</p>
            <p className="truncate text-xs text-muted-foreground">Observatory</p>
          </div>
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
        </div>
      </div>
    </div>
  )
}

function NavItemLink({ item, active }: { item: (typeof navigationGroups)[number]["items"][number] | (typeof sectionNav)[number]; active: boolean }) {
  const Icon = item.icon
  return (
    <NavLink
      to={item.href.toLocaleLowerCase()}
      className={cn(
        "group relative flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-[13px] font-medium transition-colors duration-150",
        active
          ? "bg-sidebar-accent text-sidebar-accent-foreground"
          : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
      )}
    >
      <span
        aria-hidden
        className={cn(
          "absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-gradient-to-b from-chart-1 to-chart-2 transition-opacity",
          active ? "opacity-100" : "opacity-0",
        )}
      />
      <Icon className={cn("h-4 w-4 shrink-0", active ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
      <span className="flex-1 truncate">{item.title}</span>
      {item.badge !== undefined && (
        <span className="rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
          {item.badge}
        </span>
      )}
    </NavLink>
  )
}