import { useState } from "react"
import { toast } from "sonner"
import { Camera, KeyRound, ShieldCheck } from "lucide-react"

import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function ProfilePage() {
  const [name, setName] = useState("Avery Blake")
  const [email, setEmail] = useState("avery@openops.ai")

  return (
    <div className="container max-w-4xl px-6 py-8">
      <PageHeader
        title="Profile"
        description="Manage your personal information and account security."
        eyebrow="Account"
      />

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="api">API keys</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-4 space-y-4">
          <CardShell title="Personal information">
            <div className="flex items-center gap-4">
              <span className="relative flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-chart-1 to-chart-2 text-lg font-semibold text-white">
                {name.split(" ").map((p) => p[0]).join("").slice(0, 2)}
                <button
                  className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full border bg-card text-muted-foreground hover:text-foreground"
                  aria-label="Upload photo"
                  onClick={() => toast.info("Photo upload coming soon")}
                >
                  <Camera className="h-3.5 w-3.5" />
                </button>
              </span>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">Admin</Badge>
                <Badge variant="outline">Active</Badge>
              </div>
            </div>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="p-name">Full name</Label>
                <Input id="p-name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="p-email">Email</Label>
                <Input id="p-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Timezone</Label>
                <Select defaultValue="utc">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="utc">UTC (default)</SelectItem>
                    <SelectItem value="america">America/New_York</SelectItem>
                    <SelectItem value="europe">Europe/London</SelectItem>
                    <SelectItem value="asia">Asia/Tokyo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <Button onClick={() => toast.success("Profile updated")}>Save changes</Button>
            </div>
          </CardShell>
        </TabsContent>

        <TabsContent value="security" className="mt-4 space-y-4">
          <CardShell title="Security">
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-500">
                  <ShieldCheck className="h-4 w-4" />
                </span>
                <div>
                  <p className="text-sm font-medium">Two-factor authentication</p>
                  <p className="text-xs text-muted-foreground">Add an extra layer of security to your account</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => toast.success("2FA enabled")}>
                Enable
              </Button>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-3">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-500/10 text-violet-500">
                  <KeyRound className="h-4 w-4" />
                </span>
                <div>
                  <p className="text-sm font-medium">Password</p>
                  <p className="text-xs text-muted-foreground">Last changed 30 days ago</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => toast.info("Password change form")}>
                Change
              </Button>
            </div>
          </CardShell>
        </TabsContent>

        <TabsContent value="api" className="mt-4 space-y-4">
          <CardShell title="API keys" description="Keys used to call the OpenOps API">
            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">No API keys generated yet.</p>
            </div>
            <div className="mt-4">
              <Button onClick={() => toast.info("Key generation flow")}>Generate key</Button>
            </div>
          </CardShell>
        </TabsContent>
      </Tabs>
    </div>
  )
}