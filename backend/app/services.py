"""
Stock analysis service coordinating various agents and data sources.
"""

from typing import Optional, Callable, Dict, Any
import asyncio
from datetime import datetime
import json
import logging
import os
import traceback
import yfinance as yf
from .gemini import GeminiModel
from .aperturedb import ApertureDBClient

from backend.agents.news_lookup_agent import fetch_news_links
from backend.agents.youtube_agent import fetch_stock_videos
from backend.agents.browser_context import BrowserContext
from .models import StockReport, StockData, NewsArticle, YouTubeVideo
from .cache import CacheService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class StockService:
    """Service for generating comprehensive stock analysis reports."""
    
    def __init__(self, event_handler: Optional[Callable] = None):
        """
        Initialize the stock service.
        
        Args:
            event_handler: Optional callback for streaming events during report generation
        """
        logger.debug("Initializing StockService")
        self.event_handler = event_handler
        self.browser_context = None
        self.cache = CacheService()
        logger.debug("Creating GeminiModel")
        self.model = GeminiModel()
        self.logger = logging.getLogger(__name__)
            
        # Initialize ApertureDB client
        logger.debug("Creating ApertureDB client")
        self.db = ApertureDBClient()
        logger.debug("StockService initialization complete")
    
    async def __aenter__(self):
        """Set up browser context for web scraping."""
        logger.debug("Setting up browser context")
        self.browser_context = await BrowserContext.get_instance()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        logger.debug("Cleaning up resources")
        if self.browser_context:
            await self.browser_context.close()
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event if handler is configured."""
        if self.event_handler:
            try:
                # Convert pandas Timestamp objects to ISO format strings
                data = json.loads(
                    json.dumps(data, default=lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))
                )
                self.logger.debug(f"Emitting event: {event_type}")
                self.logger.debug(f"Data: {json.dumps(data, indent=2)}")
                await self.event_handler(event_type, data)
            except Exception as e:
                self.logger.error(f"Error emitting event: {str(e)}", exc_info=True)
    
    async def generate_report(self, ticker: str) -> StockReport:
        """Generate a comprehensive stock analysis report."""
        try:
            self.logger.debug(f"Starting report generation for {ticker}")
            
            # Get stock data from yfinance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Format stock data
            stock_data = StockData(
                price=info.get('currentPrice', 0.0),
                change=f"{info.get('regularMarketChangePercent', 0.0):.2f}%",
                market_cap=f"${info.get('marketCap', 0)/1e9:.2f}B",
                pe_ratio=info.get('forwardPE', 0.0)
            )
            
            # Get news articles
            news_articles = []
            raw_news = await fetch_news_links(ticker)
            for article in raw_news[:5]:  # Limit to top 5 articles
                # Handle both datetime objects and ISO format strings
                published_at = article['published_at']
                if hasattr(published_at, 'isoformat'):
                    published_at = published_at.isoformat()
                
                news_articles.append(NewsArticle(
                    headline=article['title'],
                    summary=article['summary'],
                    url=article['url'],
                    sentiment=article['sentiment'],
                    published_at=published_at
                ))
            
            # Get YouTube videos
            youtube_videos = []
            raw_videos = await fetch_stock_videos(ticker)
            for video in raw_videos[:3]:  # Limit to top 3 videos
                # Handle both datetime objects and ISO format strings
                published_at = video['published_at']
                if hasattr(published_at, 'isoformat'):
                    published_at = published_at.isoformat()
                
                youtube_videos.append(YouTubeVideo(
                    title=video['title'],
                    url=video['url'],
                    summary=video['summary'],
                    channel=video['channel'],
                    published_at=published_at
                ))
            
            # Generate AI analysis
            analysis_data = {
                'ticker': ticker,
                'stock_data': stock_data.dict(),
                'news_articles': [n.dict() for n in news_articles],
                'youtube_videos': [v.dict() for v in youtube_videos]
            }
            
            analysis = await self.generate_market_analysis(analysis_data)
            
            # Create final report
            report = StockReport(
                ticker=ticker,
                sentiment_summary=analysis['sentiment_summary'],
                key_insights=analysis['key_insights'],
                stock_data=stock_data,
                news_articles=news_articles,
                youtube_videos=youtube_videos,
                full_report=analysis['full_report']
            )
            
            # Cache the report
            await self.cache.cache_report(ticker, report.dict())
            
            self.logger.debug("Report generation complete")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            self.logger.debug(traceback.format_exc())
            raise
    
    async def generate_market_analysis(self, analysis_data):
        prompt = f"""
        Analyze the following stock data for {analysis_data['ticker']} and provide a comprehensive market analysis:
        
        Stock Data:
        {json.dumps(analysis_data['stock_data'], indent=2)}
        
        News Articles:
        {json.dumps(analysis_data['news_articles'], indent=2)}
        
        YouTube Videos:
        {json.dumps(analysis_data['youtube_videos'], indent=2)}
        
        Format your response as a JSON object with these sections:
        - sentiment_summary: Brief summary of the overall sentiment
        - key_insights: Key insights and findings
        - full_report: Full market analysis report
        """
        
        logger.debug("Sending prompt to Gemini")
        analysis = await self.model.generate_content(prompt)
        logger.debug("Received analysis from Gemini")
        
        return json.loads(analysis)
