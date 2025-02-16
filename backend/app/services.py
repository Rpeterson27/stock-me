from datetime import datetime
from typing import List, Dict, Any
import yfinance as yf
from playwright.async_api import async_playwright
from agentql import wrap
from google.cloud import language_v2
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import asyncio
from ..agents.youtube_agent import fetch_stock_videos
from ..agents.news_lookup_agent import fetch_news_links
from ..agents.browser_context import BrowserContext
from ..agents.report_generator import StockReportGenerator

class StockService:
    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await BrowserContext.close()

    async def get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Get basic stock data from Yahoo Finance."""
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "price": info.get("currentPrice", 0.0),
            "change": f"{info.get('regularMarketChangePercent', 0.0):.2f}%",
            "market_cap": f"{info.get('marketCap', 0) / 1e12:.1f}T",
            "pe_ratio": info.get("forwardPE", 0.0)
        }

    async def get_news_articles(self, ticker: str) -> List[Dict[str, Any]]:
        """Get and analyze news articles."""
        try:
            return await fetch_news_links(ticker)
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []

    async def get_youtube_videos(self, ticker: str) -> List[Dict[str, Any]]:
        """Search and analyze YouTube videos."""
        try:
            return await fetch_stock_videos(ticker)
        except Exception as e:
            print(f"Error fetching YouTube videos: {str(e)}")
            return []

    async def generate_report(self, ticker: str) -> Dict[str, Any]:
        """Generate a comprehensive stock report."""
        try:
            # Get data from different sources concurrently
            stock_data = await self.get_stock_data(ticker)
            
            # Generate the full report using our StockReportGenerator
            report_generator = StockReportGenerator()
            full_report = await report_generator.generate_report(ticker)
            
            # Extract key insights from the report
            # Split the report into sections based on markdown headers
            sections = full_report.split('**')
            
            # Extract sentiment summary (usually in the News Sentiment section)
            sentiment_summary = "Neutral"  # Default
            for section in sections:
                if "News Sentiment" in section:
                    sentiment_lines = section.split('\n')
                    if len(sentiment_lines) > 1:
                        sentiment_summary = sentiment_lines[1].strip('* ')
            
            # Extract key insights from the Actionable Summary section
            key_insights = []
            for section in sections:
                if "Actionable Summary" in section:
                    insights = section.split('\n')
                    key_insights = [line.strip('* ') for line in insights if line.strip().startswith('*')]
            
            if not key_insights:  # Fallback if no insights found
                key_insights = ["Analysis in progress", "Check full report for details"]
            
            # Get news and videos concurrently
            news_articles, youtube_videos = await asyncio.gather(
                self.get_news_articles(ticker),
                self.get_youtube_videos(ticker)
            )
            
            return {
                "ticker": ticker,
                "sentiment_summary": sentiment_summary,
                "key_insights": key_insights,
                "stock_data": stock_data,
                "news_articles": news_articles,
                "youtube_videos": youtube_videos,
                "full_report": full_report
            }
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            raise
