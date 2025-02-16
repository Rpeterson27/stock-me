import os
import json
import logging
import yfinance as yf
from typing import Dict, Any, List
import google.generativeai as genai
from datetime import datetime, timedelta

import wandb
import weave
from .news_lookup_agent import fetch_news_links
from .news_article_scraping_agent import scrape_article_content
from .youtube_agent import fetch_stock_videos

logger = logging.getLogger(__name__)

# Initialize W&B with API key
wandb.login(key=os.getenv('WANDB_API_KEY'))

# Initialize Weave
weave.init('stock-analysis')

class StockReportGenerator:
    def __init__(self, event_handler=None):
        """Initialize the report generator.
        
        Args:
            event_handler: Optional callback function to handle progress events
        """
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        self.event_handler = event_handler
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event with data if event handler is configured."""
        if self.event_handler:
            await self.event_handler({
                "type": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            })

    async def fetch_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch comprehensive stock data using yfinance."""
        stock = yf.Ticker(ticker)
        info = stock.info
        history = stock.history(period="1mo")
        
        # Emit stock data event
        await self.emit_event("stock_data", {
            "price": info.get("regularMarketPrice"),
            "change": f"{info.get('regularMarketChangePercent', 0):.2f}%",
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("forwardPE")
        })
        
        return info, history

    @weave.op()
    async def generate_report(self, ticker: str) -> str:
        """Generate a comprehensive stock analysis report."""
        try:
            # Get stock data
            info, history = await self.fetch_stock_data(ticker)
            
            # Fetch news articles
            news_links = await fetch_news_links(ticker)
            news_articles = []
            for link in news_links[:5]:  # Process top 5 news articles
                content = await scrape_article_content(link)
                news_articles.append(content)
                # Emit news article event
                await self.emit_event("news_article", content)
            
            # Fetch YouTube videos
            videos = await fetch_stock_videos(ticker)
            for video in videos[:3]:  # Process top 3 videos
                # Emit video event
                await self.emit_event("youtube_video", video)
            
            # Prepare data for the prompt
            recent_prices = history.tail(10)[['Close']].to_dict()['Close']
            # Convert timestamps to strings
            recent_prices = {k.strftime('%Y-%m-%d'): v for k, v in recent_prices.items()}
            
            # Prepare article data with truncated content
            article_data = []
            for article in news_articles:
                content = article['content'][:1000] if len(article['content']) > 1000 else article['content']
                article_data.append({
                    'headline': article['headline'],
                    'content': content
                })
            
            # Format the data for the prompt
            prompt = f"""You are a professional stock analyst. Generate a comprehensive analysis report for {ticker} stock.
            Use the following data to create your analysis:

            Stock Information:
            - Current Price: ${info.get('currentPrice', 'N/A')}
            - Market Cap: ${info.get('marketCap', 0) / 1e9:.2f}B
            - P/E Ratio: {info.get('forwardPE', 'N/A')}
            - 52 Week Range: ${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}

            Recent Price History:
            {json.dumps(recent_prices, indent=2)}

            Recent News Articles:
            {json.dumps([{
                'headline': article.get('title', ''),
                'summary': article.get('description', ''),
                'source': article.get('source', ''),
                'time': article.get('time', '')
            } for article in news_links[:5]], indent=2)}

            Detailed Article Analysis:
            {json.dumps(article_data, indent=2)}

            Recent YouTube Coverage:
            {json.dumps([{
                'title': video.get('title', ''),
                'channel': video.get('channel', '')
            } for video in videos[:5]], indent=2)}

            Format your report with these sections:
            1. Technical Analysis
            2. News Sentiment (including insights from full article content)
            3. Social Media Analysis
            4. Fundamental Analysis
            5. Actionable Summary
            6. Potential Risks/Opportunities
            """

            # Generate report using Gemini
            response = self.model.generate_content(prompt)
            report = response.text
            
            # Emit final analysis event
            await self.emit_event("analysis", {
                "sentiment_summary": report[:200],  # First 200 chars as summary
                "full_report": report
            })
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            await self.emit_event("error", {"message": str(e)})
            raise

if __name__ == "__main__":
    import asyncio
    
    async def test():
        generator = StockReportGenerator()
        report = await generator.generate_report("AAPL")
        print(report)
    
    asyncio.run(test())
