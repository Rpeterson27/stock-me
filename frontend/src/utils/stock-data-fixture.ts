// Define the structure of our stock report
export interface StockReport {
  ticker: string
  sentiment_summary: string
  key_insights: string[]
  stock_data: {
    price: number
    change: string
    market_cap: string
    pe_ratio: number
  }
  news_articles: Array<{
    headline: string
    summary: string
    url: string
    sentiment: string
    published_at: string
  }>
  youtube_videos: Array<{
    title: string
    url: string
    summary: string
    channel: string
    published_at: string
  }>
  full_report: string
}

// Create a fixture data
const fixtureData: StockReport = {
  ticker: "AAPL",
  sentiment_summary: "Positive",
  key_insights: [
    "Strong financial performance in recent quarter",
    "New product launches expected to drive growth",
    "Potential headwinds from supply chain disruptions",
  ],
  stock_data: {
    price: 150.25,
    change: "+2.5%",
    market_cap: "2.5T",
    pe_ratio: 28.5,
  },
  news_articles: [
    {
      headline: "Apple Reports Record Q3 Earnings",
      summary: "Apple Inc. reported record-breaking third-quarter earnings, surpassing analyst expectations.",
      url: "https://example.com/apple-q3-earnings",
      sentiment: "Positive",
      published_at: "2023-07-28T18:30:00Z",
    },
    {
      headline: "Supply Chain Issues May Impact iPhone Production",
      summary: "Ongoing global supply chain disruptions could affect Apple's iPhone production targets.",
      url: "https://example.com/apple-supply-chain",
      sentiment: "Negative",
      published_at: "2023-07-26T14:15:00Z",
    },
  ],
  youtube_videos: [
    {
      title: "Apple Stock Analysis: Buy, Sell, or Hold?",
      url: "https://youtube.com/watch?v=abcdefghijk",
      summary: "In-depth analysis of Apple's current market position and future prospects.",
      channel: "Stock Market Insights",
      published_at: "2023-07-25T10:00:00Z",
    },
  ],
  full_report: "Apple Inc. (AAPL) continues to demonstrate strong financial performance...",
}

// Function to fetch stock data (simulating an API call)
export async function fetchStockData(ticker: string): Promise<StockReport> {
  // Simulate API latency
  await new Promise((resolve) => setTimeout(resolve, 500))

  // In a real application, this would be an API call to your backend
  return { ...fixtureData, ticker }
}

