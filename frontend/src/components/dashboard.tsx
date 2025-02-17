import type React from "react"
import { useState } from "react"
import { Button, Container, TextInput, Paper, Title, Grid, Text, Group } from "@mantine/core"
import { useQuery } from "@tanstack/react-query"
import { useStytch } from "@stytch/react"
import StockDetails from "./stock-details"
import YouTubeScroll from "./youtube-scroll"
import StockAnalysis from "./stock-analysis"
import { StockDetailsSkeleton } from "./skeletons/stock-details-skeleton"
import { StockAnalysisSkeleton } from "./skeletons/stock-analysis-skeleton"
import { YouTubeScrollSkeleton } from "./skeletons/youtube-scroll-skeleton"
import { fetchStockReport } from "../services/api"

interface DashboardProps {
  onLogout: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const [ticker, setTicker] = useState("")
  const stytch = useStytch()
  
  const { data: stockData, isLoading, refetch } = useQuery({
    queryKey: ["stockReport", ticker],
    queryFn: () => fetchStockReport(ticker),
    enabled: false,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (ticker) {
      refetch()
    }
  }

  console.log('Raw Stock Data:', stockData)
  console.log('Analysis Field:', stockData?.analysis)

  const parseFullReport = (report: string) => {
    const sections = {
      technical: { content: [] as string[], type: 'technical' as const, title: 'Technical Analysis' },
      fundamental: { content: [] as string[], type: 'fundamental' as const, title: 'Fundamental Analysis' },
      sentiment: { content: [] as string[], type: 'sentiment' as const, title: 'Sentiment Analysis' },
      risks: { content: [] as string[], type: 'risks' as const, title: 'Risks' },
      opportunities: { content: [] as string[], type: 'opportunities' as const, title: 'Opportunities' }
    };

    if (!report) return [];

    // Split the report into sections
    const lines = report.split('\n');
    let currentSection: keyof typeof sections | null = null;

    for (let line of lines) {
      // Remove markdown formatting and trim
      line = line.replace(/\*\*/g, '').trim();
      
      if (!line) continue; // Skip empty lines

      // Check for section headers
      if (line.toLowerCase().includes('technical analysis')) {
        currentSection = 'technical';
      } else if (line.toLowerCase().includes('fundamental analysis')) {
        currentSection = 'fundamental';
      } else if (
        line.toLowerCase().includes('news sentiment') || 
        line.toLowerCase().includes('social media analysis')
      ) {
        currentSection = 'sentiment';
      } else if (line.toLowerCase().includes('risks/opportunities')) {
        // Split risks and opportunities section
        const parts = line.split(':');
        if (parts.length > 1) {
          const [risks, opportunities] = parts[1].split(',').map(s => s.trim());
          if (risks) sections.risks.content.push(risks);
          if (opportunities) sections.opportunities.content.push(opportunities);
        }
      } else if (line.startsWith('* ') && currentSection) {
        // Add bullet points to the current section
        const content = line.replace('* ', '').trim();
        if (content) {
          sections[currentSection].content.push(content);
        }
      }
    }

    // Add the actionable summary to sentiment analysis
    if (report.includes('Actionable Summary')) {
      const summaryStart = report.indexOf('Actionable Summary');
      const summaryEnd = report.indexOf('\n\n', summaryStart);
      if (summaryStart !== -1 && summaryEnd !== -1) {
        const summary = report.slice(summaryStart, summaryEnd)
          .split('\n')
          .filter(line => line.trim() && !line.includes('Actionable Summary'))
          .map(line => line.trim())
          .join(' ');
        if (summary) {
          sections.sentiment.content.push(summary);
        }
      }
    }

    // Add risks and opportunities from their dedicated sections
    if (report.includes('Risks:')) {
      const risksStart = report.indexOf('Risks:');
      const risksEnd = report.indexOf('\n', risksStart);
      if (risksStart !== -1 && risksEnd !== -1) {
        const risks = report.slice(risksStart + 6, risksEnd).trim();
        if (risks) sections.risks.content.push(risks);
      }
    }

    if (report.includes('Opportunities:')) {
      const oppsStart = report.indexOf('Opportunities:');
      const oppsEnd = report.indexOf('\n', oppsStart);
      if (oppsStart !== -1 && oppsEnd !== -1) {
        const opps = report.slice(oppsStart + 14, oppsEnd).trim();
        if (opps) sections.opportunities.content.push(opps);
      }
    }

    // Filter out empty sections and ensure each section has at least one item
    return Object.values(sections).filter(section => section.content.length > 0);
  };

  const analysisData = stockData?.full_report 
    ? parseFullReport(stockData.full_report)
    : [];

  console.log('Parsed Analysis Data:', analysisData)

  return (
    <Paper shadow="md" p="xl">
      <Grid>
        <Grid.Col span={12}>
          <Group justify="space-between" mb="xl">
            <Title order={1}>Stock Analysis Dashboard</Title>
            <Button onClick={() => stytch.session.revoke()}>Logout</Button>
          </Group>
          {!isLoading && (
            <form onSubmit={handleSearch}>
              <Group>
                <TextInput
                  placeholder="Enter stock ticker (e.g., AAPL)"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  style={{ flex: 1 }}
                />
                <Button type="submit">Search</Button>
              </Group>
            </form>
          )}
        </Grid.Col>
        {isLoading ? (
          <Container size="lg">
            <Grid>
              <Grid.Col span={8}>
                <StockDetailsSkeleton />
                <StockAnalysisSkeleton />
              </Grid.Col>
              <Grid.Col span={4}>
                <YouTubeScrollSkeleton />
              </Grid.Col>
            </Grid>
          </Container>
        ) : stockData ? (
          <Container size="lg">
            <Grid>
              <Grid.Col span={8}>
                <StockDetails
                  stock={{
                    symbol: stockData.ticker,
                    price: stockData.stock_data?.price || 0,
                    percentageChange: parseFloat(stockData.stock_data?.change?.replace('%', '') || '0'),
                    marketCap: stockData.stock_data?.market_cap || 'N/A',
                    peRatio: stockData.stock_data?.pe_ratio || 0,
                    sentiment: stockData.sentiment_summary || 'neutral'
                  }}
                />
                <StockAnalysis sections={analysisData} />
              </Grid.Col>
              <Grid.Col span={4}>
                <YouTubeScroll videos={stockData.youtube_videos} />
              </Grid.Col>
            </Grid>
          </Container>
        ) : null}
      </Grid>
    </Paper>
  )
}

export default Dashboard
