import { Command, ChevronDown } from "lucide-react"
import * as React from "react"
import { useNavigate } from "react-router-dom"

import { Button } from "@/components/ui/button"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import { ThemeToggle } from "@/components/theme-toggle"
import { useAppShell } from "@/components/layout/app-shell-provider"
import { navigationGroups, sectionNav } from "@/config/navigation"

export function CommandPalette() {
  const [open, setOpen] = React.useState(false)
  const navigate = useNavigate()

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const run = (path: string) => {
    setOpen(false)
    navigate(path)
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="group flex h-9 w-56 items-center gap-2 rounded-lg border bg-muted/30 px-3 text-sm text-muted-foreground transition-all hover:border-primary/30 hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:w-64"
        aria-label="Open command palette"
      >
        <SearchIcon />
        <span className="flex-1 text-left">Search or jump to…</span>
        <kbd className="pointer-events-none hidden items-center gap-1 rounded border bg-background px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground sm:inline-flex">
          <Command className="h-3 w-3" />K
        </kbd>
      </button>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Type a command or search…" />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          {navigationGroups.map((group) => (
            <CommandGroup key={group.label} heading={group.label}>
              {group.items.map((item) => {
                const Icon = item.icon
                return (
                  <CommandItem key={item.href} onSelect={() => run(item.href)}>
                    <Icon className="mr-2 h-4 w-4" />
                    {item.title}
                  </CommandItem>
                )
              })}
            </CommandGroup>
          ))}
          <CommandSeparator />
          <CommandGroup heading="Account">
            {sectionNav.map((item) => {
              const Icon = item.icon
              return (
                <CommandItem key={item.href} onSelect={() => run(item.href)}>
                  <Icon className="mr-2 h-4 w-4" />
                  {item.title}
                </CommandItem>
              )
            })}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  )
}

function SearchIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
      <path d="m20 20-3-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b glass px-4 sm:px-6">
      <div className="flex items-center gap-2 lg:hidden">
        <MobileMenuButton />
      </div>
      <CommandPalette />

      <div className="ml-auto flex items-center gap-2">
        <SystemStatusBadge />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  )
}

function SystemStatusBadge() {
  return (
    <div className="hidden items-center gap-2 rounded-lg border bg-card/60 px-2.5 py-1.5 sm:flex">
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
      </span>
      <span className="text-xs font-medium text-muted-foreground">All systems operational</span>
    </div>
  )
}

function UserMenu() {
  return (
    <Button variant="ghost" className="h-9 gap-2 px-2" aria-label="Account menu">
      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-chart-1 to-chart-2 text-[11px] font-semibold text-white">
        ab
      </span>
      <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
    </Button>
  )
}

function MobileMenuButton() {
  const { setMobileNavOpen } = useAppShell()
  return (
    <Button variant="ghost" size="icon" aria-label="Open navigation" onClick={() => setMobileNavOpen(true)}>
      <MenuIcon />
    </Button>
  )
}

function MenuIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}