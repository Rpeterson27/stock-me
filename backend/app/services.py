"""
Stock analysis service coordinating various agents and data sources.
"""

from typing import Optional, Callable, Dict, Any
import asyncio
from datetime import datetime
import json
import logging
import os
from .gemini import GeminiModel
from .aperturedb import ApertureDBClient

from backend.agents.news_lookup_agent import fetch_news_links
from backend.agents.youtube_agent import fetch_stock_videos
from backend.agents.browser_context import BrowserContext
from .models import StockReport
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
        """
        Generate a comprehensive stock analysis report.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            StockReport object containing analysis results
        """
        logger.debug(f"Generating report for {ticker}")
        
        # Check ApertureDB cache first
        logger.debug("Checking ApertureDB cache")
        cached_report = await self.db.get_cached_report(ticker)
        if cached_report:
            logger.debug(f"Using cached report for {ticker} from ApertureDB")
            await self._emit_event("analysis", cached_report)
            return StockReport(**cached_report)
        
        # Get stock data
        logger.debug("Fetching stock data")
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        # Convert Timestamp objects to ISO format strings
        def convert_timestamps(obj):
            logger.debug(f"Converting object type: {type(obj)}")
            if hasattr(obj, 'to_dict'):
                logger.debug("Object has to_dict method")
                result = {}
                for k, v in obj.to_dict().items():
                    logger.debug(f"Processing key: {k}, value type: {type(v)}")
                    result[str(k) if hasattr(k, 'isoformat') else k] = convert_timestamps(v)
                return result
            elif hasattr(obj, 'isoformat'):
                logger.debug("Converting datetime-like object to ISO format")
                return obj.isoformat()
            elif isinstance(obj, dict):
                logger.debug("Converting dictionary")
                return {str(k) if hasattr(k, 'isoformat') else k: convert_timestamps(v) for k, v in obj.items()}
            return obj
        
        logger.debug("Processing stock data")
        stock_data = {}
        
        # Process each component separately with logging
        logger.debug("Processing info")
        stock_data["info"] = stock.info
        
        logger.debug("Processing history")
        history = stock.history(period="1mo")
        logger.debug(f"History index type: {type(history.index)}")
        logger.debug(f"History columns: {history.columns}")
        stock_data["history"] = convert_timestamps(history)
        
        logger.debug("Processing balance sheet")
        if stock.balance_sheet is not None:
            logger.debug(f"Balance sheet index type: {type(stock.balance_sheet.index)}")
            stock_data["balance_sheet"] = convert_timestamps(stock.balance_sheet)
        else:
            stock_data["balance_sheet"] = None
            
        logger.debug("Processing cashflow")
        if stock.cashflow is not None:
            logger.debug(f"Cashflow index type: {type(stock.cashflow.index)}")
            stock_data["cashflow"] = convert_timestamps(stock.cashflow)
        else:
            stock_data["cashflow"] = None
            
        logger.debug("Processing earnings")
        if stock.earnings is not None:
            logger.debug(f"Earnings index type: {type(stock.earnings.index)}")
            stock_data["earnings"] = convert_timestamps(stock.earnings)
        else:
            stock_data["earnings"] = None
            
        logger.debug("Processing financials")
        if stock.financials is not None:
            logger.debug(f"Financials index type: {type(stock.financials.index)}")
            stock_data["financials"] = convert_timestamps(stock.financials)
        else:
            stock_data["financials"] = None
            
        logger.debug("Stock data processing complete")
        
        # Cache stock data
        logger.debug("Caching stock data")
        await self.cache.set("stock_data", ticker, stock_data)
        
        await self._emit_event("stock_data", stock_data)
        
        # Get news articles
        logger.debug("Fetching news articles")
        news_links = await fetch_news_links(ticker)
        await self._emit_event("news_links", {"links": news_links})
        
        # Get YouTube videos
        logger.debug("Fetching YouTube videos")
        videos = await fetch_stock_videos(ticker)
        await self._emit_event("youtube_videos", {"videos": videos})
        
        # Generate market analysis using Gemini
        logger.debug("Generating market analysis with Gemini")
        prompt = f"""
        Analyze the following stock data for {ticker} and provide a comprehensive market analysis:
        
        Stock Info:
        {json.dumps(stock_data, indent=2)}
        
        News Links:
        {json.dumps(news_links, indent=2)}
        
        YouTube Videos:
        {json.dumps(videos, indent=2)}
        
        Format your response as a JSON object with these sections:
        - summary: Brief overview of the stock's current state
        - technical_analysis: Key technical indicators and patterns
        - fundamental_analysis: Important fundamental factors
        - news_sentiment: Analysis of recent news coverage
        - risks: Potential risks and challenges
        - opportunities: Growth opportunities and positive factors
        - recommendation: Overall investment recommendation
        """
        
        logger.debug("Sending prompt to Gemini")
        analysis = await self.model.generate_content(prompt)
        logger.debug("Received analysis from Gemini")
        
        # Create final report
        logger.debug("Creating final report")
        report = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "stock_data": stock_data,
            "news_links": news_links,
            "videos": videos,
            "analysis": json.loads(analysis)
        }
        
        # Cache in ApertureDB
        logger.debug("Caching report in ApertureDB")
        await self.db.cache_report(ticker, report)
        
        await self._emit_event("analysis", report)
        logger.debug("Report generation complete")
        return StockReport(**report)
