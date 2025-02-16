from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockData(BaseModel):
    price: float
    change: str
    market_cap: str
    pe_ratio: float

class NewsArticle(BaseModel):
    headline: str
    summary: str
    url: HttpUrl
    sentiment: str
    published_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class YouTubeVideo(BaseModel):
    title: str
    url: HttpUrl
    summary: str
    channel: str
    published_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StockReport(BaseModel):
    """Model for a comprehensive stock analysis report."""
    ticker: str
    timestamp: str
    stock_data: Dict[str, Any]
    news_links: List[Dict[str, Any]]
    videos: List[Dict[str, Any]]
    analysis: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
