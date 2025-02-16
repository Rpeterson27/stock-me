"use client"

import type React from "react"
import { useEffect } from "react"
import { useStytch } from "@stytch/react"
import { Container, Loader } from "@mantine/core"

interface AuthCallbackProps {
  onSuccess: () => void
  onError: () => void
}

const AuthCallback: React.FC<AuthCallbackProps> = ({ onSuccess, onError }) => {
  const stytchClient = useStytch()

  useEffect(() => {
    const authenticateToken = async () => {
      const params = new URLSearchParams(window.location.search)
      const token = params.get("token")

      if (!token) {
        console.error("No token found in URL")
        onError()
        return
      }

      try {
        await stytchClient.oauth.authenticate(token, {
          session_duration_minutes: 60,
        })
        onSuccess()
      } catch (error) {
        console.error("Error authenticating token:", error)
        onError()
      }
    }

    authenticateToken()
  }, [stytchClient, onSuccess, onError])

  return (
    <Container style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <Loader size="xl" />
    </Container>
  )
}

export default AuthCallback

