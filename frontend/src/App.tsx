"use client"

import { useState, useEffect } from "react"
import { MantineProvider } from "@mantine/core"
import { StytchProvider } from "@stytch/react"
import { StytchUIClient } from "@stytch/vanilla-js"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import Login from "./components/login"
import Dashboard from "./components/dashboard"
import AuthCallback from "./components/auth-callback"
import styles from "./app.module.css"

const STYTCH_PUBLIC_TOKEN = process.env.REACT_APP_STYTCH_PUBLIC_TOKEN
if (!STYTCH_PUBLIC_TOKEN) {
  throw new Error("Missing REACT_APP_STYTCH_PUBLIC_TOKEN environment variable")
}

// Initialize Stytch client
const stytchClient = new StytchUIClient(STYTCH_PUBLIC_TOKEN)

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // Data is fresh for 5 minutes
      gcTime: 1000 * 60 * 30, // Cache is kept for 30 minutes
    },
  },
})

function App() {
  const [currentPage, setCurrentPage] = useState<string>(() => {
    const path = window.location.pathname
    if (path === "/authenticate") return "authenticate"
    return "login"
  })

  // Update page based on URL changes
  useEffect(() => {
    const handleRouteChange = () => {
      const path = window.location.pathname
      if (path === "/authenticate") {
        setCurrentPage("authenticate")
      }
    }

    window.addEventListener("popstate", handleRouteChange)
    return () => window.removeEventListener("popstate", handleRouteChange)
  }, [])

  const renderPage = () => {
    switch (currentPage) {
      case "login":
        return <Login onLogin={() => setCurrentPage("dashboard")} />
      case "dashboard":
        return <Dashboard onLogout={() => setCurrentPage("login")} />
      case "authenticate":
        return <AuthCallback onSuccess={() => setCurrentPage("dashboard")} onError={() => setCurrentPage("login")} />
      default:
        return <Login onLogin={() => setCurrentPage("dashboard")} />
    }
  }

  return (
    <QueryClientProvider client={queryClient}>
      <StytchProvider stytch={stytchClient}>
        <MantineProvider>
          <div className={styles.app}>{renderPage()}</div>
        </MantineProvider>
      </StytchProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

export default App
