interface StockReport {
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

export async function fetchStockReport(ticker: string): Promise<StockReport> {
  const response = await fetch(`http://localhost:8000/report/${ticker}`, {
    method: "POST",
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch stock report: ${response.statusText}`)
  }

  return response.json()
}
