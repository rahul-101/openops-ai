import * as React from "react"
import { createRoot } from "react-dom/client"

import { Providers } from "@/app/providers"
import { AppRoutes } from "@/app/router"
import "@/index.css"

function Root() {
  return (
    <React.StrictMode>
      <Providers>
        <AppRoutes />
      </Providers>
    </React.StrictMode>
  )
}

createRoot(document.getElementById("root")!).render(<Root />)