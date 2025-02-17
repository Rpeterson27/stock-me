from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class NewsArticle(BaseModel):
    headline: str
    summary: str
    url: str
    sentiment: str
    published_at: str  # ISO 8601 format

class YouTubeVideo(BaseModel):
    title: str
    url: str
    summary: str
    channel: str
    published_at: str  # ISO 8601 format

class StockData(BaseModel):
    price: float
    change: str
    market_cap: str
    pe_ratio: float

class StockReport(BaseModel):
    """Model for a comprehensive stock analysis report."""
    ticker: str
    sentiment_summary: str
    key_insights: List[str]
    stock_data: StockData
    news_articles: List[NewsArticle]
    youtube_videos: List[YouTubeVideo]
    full_report: str
