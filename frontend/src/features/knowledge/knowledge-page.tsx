import { useQuery } from "@tanstack/react-query"
import { FileText, Plus, Search, ScrollText } from "lucide-react"
import { useState } from "react"

import { feClient } from "@/services/api"
import { PageHeader } from "@/components/shared/page-header"
import { CardShell } from "@/components/shared/card-shell"
import { EmptyState, LoadingState } from "@/components/shared/states"
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
import { Textarea } from "@/components/ui/textarea"
import { useDebounceValue } from "@/hooks/use-hooks"
import { formatDateTime, titleCase } from "@/lib/utils"
import type { KnowledgeDocument } from "@/types/api"

export function KnowledgePage() {
  const [search, setSearch] = useState("")
  const debounced = useDebounceValue(search, 400)

  const docs = useQuery({
    queryKey: ["knowledge", "search", debounced],
    queryFn: () =>
      debounced.trim()
        ? feClient.get<KnowledgeDocument[]>(`/knowledge/search?q=${encodeURIComponent(debounced.trim())}`)
        : Promise.resolve([] as KnowledgeDocument[]),
    enabled: Boolean(debounced.trim()),
  })

  const documents = useQuery({
    queryKey: ["knowledge", "documents"],
    queryFn: () => feClient.get<KnowledgeDocument[]>("/knowledge/documents"),
  })

  const [stored, setStored] = useState<KnowledgeDocument[]>([])

  const merged = [...(documents.data ?? []), ...stored].filter(
    (doc, i, arr) => arr.findIndex((d) => d.id === doc.id && d.title === doc.title) === i,
  )

  return (
    <div className="container px-6 py-8">
      <PageHeader
        title="Knowledge Base"
        description="Search runbooks, resolutions and incident memory with semantic retrieval."
        eyebrow="Intelligence"
        action={<StoreDocumentDialog onStored={(d) => setStored((prev) => [d, ...prev])} />}
      />

      <div className="mb-4 relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Semantic search across runbooks and resolutions…"
          className="pl-9"
        />
      </div>

      <CardShell title={debounced ? `Results for "${debounced}"` : "Knowledge documents"} description={debounced ? "Semantic search results" : "Stored runbooks and resolutions"}>
        <KnowledgeResults searchActive={Boolean(debounced.trim())} query={debounced} results={docs.data ?? []} loading={docs.isFetching} stored={merged} storedLoading={documents.isPending} />
      </CardShell>
    </div>
  )
}

function KnowledgeResults({
  searchActive,
  query,
  results,
  loading,
  stored,
  storedLoading,
}: {
  searchActive: boolean
  query: string
  results: KnowledgeDocument[]
  loading: boolean
  stored: KnowledgeDocument[]
  storedLoading?: boolean
}) {
  if (searchActive && loading) return <LoadingState label="Searching knowledge base…" className="min-h-[240px]" />
  if (searchActive && !results.length && !loading)
    return <EmptyState title="No matches" description={`No knowledge found for "${query}".`} className="min-h-[240px]" />
  if (storedLoading) return <LoadingState label="Loading documents…" className="min-h-[240px]" />
  if (!searchActive && !stored.length)
    return (
      <EmptyState
        title="No documents yet"
        description="Store runbooks and resolutions to build your knowledge base."
        className="min-h-[240px]"
      />
    )

  const items = searchActive ? results : stored
  return (
    <div className="grid gap-3 lg:grid-cols-2">
      {items.map((doc) => (
        <div key={doc.id ?? doc.title} className="rounded-lg border p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              {doc.type === "runbook" ? (
                <ScrollText className="h-4 w-4 text-violet-500" />
              ) : (
                <FileText className="h-4 w-4 text-emerald-500" />
              )}
              <p className="text-sm font-medium">{doc.title}</p>
            </div>
            <Badge variant="outline">{titleCase(doc.type)}</Badge>
          </div>
          <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-sm text-muted-foreground">{doc.content}</p>
          <p className="mt-2 text-xs text-muted-foreground">
            {doc.created_at ? formatDateTime(doc.created_at) : "Stored locally"}
          </p>
        </div>
      ))}
    </div>
  )
}

function StoreDocumentDialog({ onStored }: { onStored: (d: KnowledgeDocument) => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [type, setType] = useState("runbook")
  const [busy, setBusy] = useState(false)

  async function store() {
    if (!title.trim() || !content.trim()) return
    setBusy(true)
    try {
      const doc = await feClient.post<KnowledgeDocument>("/knowledge/runbooks", {
        title: title.trim(),
        content: content.trim(),
        metadata: { type },
      })
      onStored(doc)
      setOpen(false)
      setTitle("")
      setContent("")
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add document
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Store knowledge</DialogTitle>
          <DialogDescription>Add a runbook or resolution to the knowledge base.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="kb-type">Type</Label>
            <select
              id="kb-type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="runbook">Runbook</option>
              <option value="resolution">Resolution</option>
              <option value="incident">Incident</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="kb-title">Title</Label>
            <Input id="kb-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Kafka consumer lag recovery" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="kb-content">Content</Label>
            <Textarea id="kb-content" value={content} onChange={(e) => setContent(e.target.value)} rows={5} placeholder="Document the procedure…" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={store} disabled={busy || !title.trim() || !content.trim()}>
            {busy ? "Storing…" : "Store"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}