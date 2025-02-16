import type React from "react"
import { useState } from "react"
import { Button, Container, TextInput, Paper, Title, Grid, Text, Loader, Group } from "@mantine/core"
import { useQuery } from "@tanstack/react-query"
import { useStytch } from "@stytch/react"
import StockDetails from "./stock-details"
import YouTubeScroll from "./youtube-scroll"
import { fetchStockReport } from "../services/api"
import styles from "./dashboard.module.css"

interface DashboardProps {
  onLogout: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [stockSymbol, setStockSymbol] = useState("")
  const stytchClient = useStytch()

  const {
    data: stockData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["stockReport", stockSymbol],
    queryFn: () => fetchStockReport(stockSymbol),
    enabled: false, // Don't fetch automatically
  })

  const handleSearch = () => {
    if (!stockSymbol) {
      return
    }
    refetch()
  }

  const handleLogout = async () => {
    try {
      await stytchClient.session.revoke()
      onLogout()
    } catch (error) {
      console.error("Failed to logout:", error)
    }
  }

  return (
    <Container size="xl" my={40}>
      <Paper withBorder shadow="md" p={30} radius="md">
        <Grid>
          <Grid.Col span={12}>
            <Group justify="space-between">
              <Title order={2}>Stock Analysis Dashboard</Title>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </Group>
          </Grid.Col>
          <Grid.Col span={12}>
            <Group>
              <TextInput
                value={stockSymbol}
                onChange={(e) => setStockSymbol(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., AAPL)"
                size="md"
                style={{ flex: 1 }}
              />
              <Button onClick={handleSearch} size="md" loading={isLoading}>
                Search
              </Button>
            </Group>
            {error instanceof Error && (
              <Text c="red" size="sm" mt="sm">
                {error.message}
              </Text>
            )}
          </Grid.Col>
          {isLoading ? (
            <Grid.Col span={12} style={{ textAlign: "center" }}>
              <Loader size="xl" />
            </Grid.Col>
          ) : stockData ? (
            <>
              <Grid.Col span={8}>
                <StockDetails
                  price={stockData.stock_data.price}
                  change={stockData.stock_data.change}
                  market_cap={stockData.stock_data.market_cap}
                  pe_ratio={stockData.stock_data.pe_ratio}
                  sentiment={stockData.sentiment_summary}
                />
                <Paper withBorder shadow="md" p="md" mt="lg">
                  <Title order={3} mb="md">Key Insights</Title>
                  <ul>
                    {stockData.key_insights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </Paper>
                <Paper withBorder shadow="md" p="md" mt="lg">
                  <Title order={3} mb="md">Full Analysis</Title>
                  <Text>{stockData.full_report}</Text>
                </Paper>
              </Grid.Col>
              <Grid.Col span={4}>
                <YouTubeScroll videos={stockData.youtube_videos} />
              </Grid.Col>
            </>
          ) : null}
        </Grid>
      </Paper>
    </Container>
  )
}

export default Dashboard
