import type React from "react"
import { useStytch } from "@stytch/react"
import { Button, Container, Paper, Title, Text } from "@mantine/core"
import { BrandGoogle } from "tabler-icons-react"

interface LoginProps {
  onLogin: () => void
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const stytchClient = useStytch()

  const handleGoogleLogin = async () => {
    try {
      await stytchClient.oauth.google.start({
        login_redirect_url: `${window.location.origin}/authenticate`,
        signup_redirect_url: `${window.location.origin}/authenticate`,
      })
    } catch (error) {
      console.error("Failed to start Google OAuth:", error)
    }
  }

  return (
    <Container size={420} my={40}>
      <Title ta="center" fw={900}>
        Welcome to Stock Analysis
      </Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Sign in to access your dashboard
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <Button
          leftSection={<BrandGoogle size={20} />}
          variant="default"
          color="gray"
          fullWidth
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </Button>
      </Paper>
    </Container>
  )
}

export default Login
