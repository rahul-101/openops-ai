import { useEffect, useRef, useState } from "react"

export interface UseSseOptions {
  enabled?: boolean
  onEvent?: (event: unknown) => void
  onError?: (error: Event) => void
}

/**
 * Subscribe to the operations SSE stream with automatic reconnect.
 */
export function useSse(url: string, { enabled = true, onEvent, onError }: UseSseOptions = {}) {
  const [connected, setConnected] = useState(false)
  const live = useRef(true)
  const handlers = useRef({ onEvent, onError })
  handlers.current = { onEvent, onError }

  useEffect(() => {
    live.current = enabled
    if (!enabled) {
      setConnected(false)
      return
    }

    let source: EventSource | null = null
    let retries = 0
    let stop = false

    const connect = () => {
      if (stop || !live.current) return
      source = new EventSource(url)

      source.onopen = () => {
        retries = 0
        setConnected(true)
      }
      source.onmessage = (ev) => {
        try {
          handlers.current.onEvent?.(JSON.parse(ev.data))
        } catch {
          /* ignore malformed */
        }
      }
      source.onerror = (err) => {
        setConnected(false)
        handlers.current.onError?.(err)
        source?.close()
        if (stop || !live.current) return
        const delay = Math.min(1000 * 2 ** retries, 15_000)
        retries += 1
        setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      stop = true
      source?.close()
      setConnected(false)
    }
  }, [url, enabled])

  return { connected }
}