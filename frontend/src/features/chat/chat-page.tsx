import { motion } from "framer-motion"
import { Bot, Paperclip, Send, Sparkles, User, X } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

import { feClient } from "@/services/api"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  pending?: boolean
  error?: boolean
}

const SUGGESTIONS = [
  "Summarize the current incident posture",
  "What agents are available and how do they behave?",
  "Explain the risk-based execution policy",
  "Draft a post-incident review template",
]

const BOOTSTRAP: Message[] = [
  {
    id: "boot-1",
    role: "assistant",
    content:
      "I'm your **OpenOps AI** copilot. I can reason over your incidents, explain agent behavior, and help you operate the platform.\n\nTry asking me to:\n- **Summarize** current incidents or a specific alert\n- **Explain** the autonomous decision pipeline\n- **Guide** you through risk-gated remediation\n\n_Streaming, markdown and code blocks are enabled._",
  },
]

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function simulateStream(full: string, onChunk: (chunk: string) => void) {
  // Reveal the real backend response incrementally for a streaming feel
  const chunks = full.split(/(?<=\s)/)
  for (const chunk of chunks) {
    onChunk(chunk)
    await delay(12)
  }
}

export function AiChatPage() {
  const [messages, setMessages] = useState<Message[]>(BOOTSTRAP)
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages])

  async function send(text: string) {
    const trimmed = text.trim()
    if (!trimmed || streaming) return
    setInput("")
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: trimmed }
    const assistantMsg: Message = { id: crypto.randomUUID(), role: "assistant", content: "", pending: true }
    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setStreaming(true)

    try {
      const res = await feClient.post<{ reply: string }>("/chat", {
        message: trimmed,
      })
      const full = res.reply || "I didn't get a response. Try asking about your incidents, playbooks, or a specific event."
      await simulateStream(full, (chunk) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, content: m.content + chunk, pending: false } : m,
          ),
        )
      })
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong."
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantMsg.id ? { ...m, content: msg, pending: false, error: true } : m)),
      )
    } finally {
      setMessages((prev) => prev.map((m) => (m.id === assistantMsg.id ? { ...m, pending: false } : m)))
      setStreaming(false)
      textareaRef.current?.focus()
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-4 py-4">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-chart-1 to-chart-2 text-white">
              <Sparkles className="h-4 w-4" />
            </span>
            <div>
              <h1 className="text-sm font-semibold">AI Copilot</h1>
              <p className="text-xs text-muted-foreground">Reason over your operations with OpenOps AI</p>
            </div>
          </div>
          {streaming && (
            <span className="inline-flex items-center gap-1.5 rounded-full border bg-muted/40 px-2.5 py-1 text-xs text-muted-foreground">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-violet-500" />
              Thinking…
            </span>
          )}
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto pb-6">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              layout="position"
            >
              <MessageBubble message={msg} />
            </motion.div>
          ))}
          {!messages.some((m) => m.pending && !m.content) && messages.length === 1 && (
            <div className="space-y-2 pt-2">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Suggested prompts
              </p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-lg border bg-card px-3 py-2 text-left text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Composer */}
        <div className="shrink-0 border-t pt-4">
          <div className="relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask about incidents, agents, policies…"
              className="min-h-[52px] resize-none pr-24"
              rows={1}
            />
            <div className="absolute bottom-2 right-2 flex items-center gap-1">
              <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Attach context">
                <Paperclip className="h-4 w-4" />
              </Button>
              <Button
                size="icon"
                className="h-8 w-8"
                onClick={() => send(input)}
                disabled={streaming || !input.trim()}
                aria-label="Send message"
              >
                {streaming ? <X className="h-4 w-4" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            Answers are grounded in live platform data via the reasoning pipeline and may be inaccurate. Verify critical actions before approving.
          </p>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"
  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <span
        className={cn(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-md",
          isUser ? "bg-secondary text-foreground" : "bg-gradient-to-br from-chart-1 to-chart-2 text-white",
        )}
      >
        {isUser ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
      </span>
      <div className={cn("max-w-[85%] space-y-2", isUser && "text-right")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "rounded-tr-sm bg-primary text-primary-foreground"
              : "rounded-tl-sm border bg-card",
          )}
        >
          {message.content ? (
            <div className={cn("markdown", isUser && "text-inherit")}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          ) : (
            <TypingIndicator />
          )}
          {message.error && !isUser && (
            <p className="mt-1 text-xs font-medium text-red-500">Request failed — check the backend connection.</p>
          )}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <span className="inline-flex items-center gap-1">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground/60"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </span>
  )
}