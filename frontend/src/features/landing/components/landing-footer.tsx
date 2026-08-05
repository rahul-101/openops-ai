import { Github, Linkedin, Twitter } from "lucide-react"
import { Link } from "react-router-dom"

import { Logo } from "@/components/shared/logo"

const COLUMNS = [
  {
    title: "Product",
    links: [
      { label: "Features", href: "#features" },
      { label: "How it works", href: "#how-it-works" },
      { label: "Architecture", href: "#architecture" },
      { label: "Integrations", href: "#security" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "#top" },
      { label: "Blog", href: "#top" },
      { label: "Careers", href: "#top" },
      { label: "Contact", href: "#top" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "/docs" },
      { label: "API reference", href: "/docs/api" },
      { label: "Status", href: "/health" },
      { label: "Security", href: "#security" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy", href: "#top" },
      { label: "Terms", href: "#top" },
      { label: "DPA", href: "#top" },
      { label: "SOC 2", href: "#top" },
    ],
  },
]

const SOCIALS = [
  { icon: Twitter, label: "Twitter" },
  { icon: Github, label: "GitHub" },
  { icon: Linkedin, label: "LinkedIn" },
]

export function LandingFooter() {
  return (
    <footer className="border-t border-border/60 bg-background/60 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_repeat(4,1fr)]">
          <div>
            <Link to="/" aria-label="OpenOps AI home">
              <Logo />
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Autonomous incident response for modern platforms. Detect, diagnose and fix — without waking your team.
            </p>
            <div className="mt-5 flex items-center gap-2">
              {SOCIALS.map(({ icon: Icon, label }) => (
                <a
                  key={label}
                  href="#top"
                  aria-label={label}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-border/60 text-muted-foreground transition-colors hover:border-chart-2/40 hover:text-foreground"
                >
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <p className="text-sm font-semibold">{col.title}</p>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border/60 pt-6 text-xs text-muted-foreground sm:flex-row">
          <p>© {new Date().getFullYear()} OpenOps AI. All rights reserved.</p>
          <p>Built for operators who value their sleep.</p>
        </div>
      </div>
    </footer>
  )
}
