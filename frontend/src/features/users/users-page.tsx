import { ShieldCheck, ShieldAlert, Shield, Search, UserPlus } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { StatCard } from "@/components/shared/stat-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { MoreHorizontal } from "lucide-react"

type Role = "Admin" | "Operator" | "Viewer"
type Status = "active" | "invited" | "suspended"

interface User {
  id: string
  name: string
  email: string
  role: Role
  status: Status
  lastActive?: string
}

const seedUsers: User[] = [
  { id: "u1", name: "Avery Blake", email: "avery@openops.ai", role: "Admin", status: "active", lastActive: "2m ago" },
  { id: "u2", name: "Jordan Lee", email: "jordan@openops.ai", role: "Operator", status: "active", lastActive: "1h ago" },
  { id: "u3", name: "Casey Morgan", email: "casey@openops.ai", role: "Operator", status: "active", lastActive: "3h ago" },
  { id: "u4", name: "Riley Chen", email: "riley@openops.ai", role: "Viewer", status: "invited", lastActive: undefined },
  { id: "u5", name: "Sam Rivera", email: "sam@openops.ai", role: "Viewer", status: "suspended", lastActive: "12d ago" },
]

const roleIcon: Record<Role, typeof Shield> = {
  Admin: ShieldCheck,
  Operator: Shield,
  Viewer: ShieldAlert,
}

const roleStyles: Record<Role, string> = {
  Admin: "border-transparent bg-violet-500/15 text-violet-600 dark:text-violet-400",
  Operator: "border-transparent bg-sky-500/15 text-sky-600 dark:text-sky-400",
  Viewer: "border-transparent bg-muted text-muted-foreground",
}

export function UsersPage() {
  const [users, setUsers] = useState<User[]>(seedUsers)
  const [query, setQuery] = useState("")

  const filtered = users.filter((u) =>
    [u.name, u.email, u.role].some((v) => v.toLowerCase().includes(query.toLowerCase())),
  )

  const active = users.filter((u) => u.status === "active").length

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Users & Roles"
        description="Manage access, roles and permissions for your workspace."
        eyebrow="Platform"
        action={<InviteUserDialog onInvited={(u) => setUsers((prev) => [...prev, u])} />}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total users" value={users.length} icon={ShieldCheck} accent="primary" hint="in workspace" />
        <StatCard label="Active" value={active} icon={Shield} accent="success" hint="active accounts" />
        <StatCard label="Admins" value={users.filter((u) => u.role === "Admin").length} icon={ShieldCheck} accent="accent" hint="full access" />
        <StatCard label="Invited" value={users.filter((u) => u.status === "invited").length} icon={ShieldAlert} accent="warning" hint="pending" />
      </div>

      <div className="mt-4">
        <CardShell title="Members" description="Everyone with access to this workspace">
          <div className="relative mb-4 max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search members…" className="pl-9" />
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last active</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-chart-1 to-chart-2 text-[11px] font-semibold text-white">
                        {u.name.split(" ").map((p) => p[0]).join("").slice(0, 2)}
                      </span>
                      <div>
                        <p className="font-medium">{u.name}</p>
                        <p className="text-xs text-muted-foreground">{u.email}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={roleStyles[u.role]}>
                      {roleIcon[u.role] && null}
                      {u.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <StatusPill status={u.status} />
                  </TableCell>
                  <TableCell className="text-muted-foreground">{u.lastActive ?? "—"}</TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" aria-label={`Actions for ${u.name}`}>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => toast.info("Edit role")}>Edit role</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => toast.info("View audit")}>View audit log</DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => setUsers((prev) => prev.map((x) => (x.id === u.id ? { ...x, status: "suspended" } : x)))}>
                          Suspend
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardShell>
      </div>
    </div>
  )
}

function StatusPill({ status }: { status: Status }) {
  const map = {
    active: "border-transparent bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
    invited: "border-transparent bg-amber-500/15 text-amber-600 dark:text-amber-400",
    suspended: "border-transparent bg-destructive/15 text-red-600 dark:text-red-400",
  } as const
  return (
    <Badge className={map[status]}>
      <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-current opacity-70" />
      {status}
    </Badge>
  )
}

function InviteUserDialog({ onInvited }: { onInvited: (u: User) => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [role, setRole] = useState<Role>("Viewer")

  function invite() {
    if (!name.trim() || !email.trim()) {
      toast.error("Name and email are required")
      return
    }
    onInvited({
      id: crypto.randomUUID(),
      name: name.trim(),
      email: email.trim(),
      role,
      status: "invited",
    })
    toast.success("Invitation sent")
    setOpen(false)
    setName("")
    setEmail("")
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <UserPlus className="mr-2 h-4 w-4" />
          Invite user
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Invite user</DialogTitle>
          <DialogDescription>Send a workspace invitation with a role.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="inv-name">Name</Label>
            <Input id="inv-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Morgan" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="inv-email">Email</Label>
            <Input id="inv-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="alex@company.com" />
          </div>
          <div className="space-y-1.5">
            <Label>Role</Label>
            <Select value={role} onValueChange={(v) => setRole(v as Role)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Admin">Admin</SelectItem>
                <SelectItem value="Operator">Operator</SelectItem>
                <SelectItem value="Viewer">Viewer</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={invite}>Send invite</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}