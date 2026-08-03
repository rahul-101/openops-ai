import * as React from "react"

/** Returns true once a short delay has elapsed (for skeleton vs content transitions). */
export function useDebounceValue<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = React.useState(value)
  React.useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return debounced
}

export function useIsMounted(): boolean {
  const mounted = React.useRef(false)
  React.useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])
  return mounted.current
}

export function useInterval(callback: () => void, delayMs: number | null) {
  const saved = React.useRef(callback)
  React.useEffect(() => {
    saved.current = callback
  }, [callback])
  React.useEffect(() => {
    if (delayMs === null) return
    const id = setInterval(() => saved.current(), delayMs)
    return () => clearInterval(id)
  }, [delayMs])
}