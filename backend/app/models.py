from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
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
    ticker: str
    sentiment_summary: str
    key_insights: List[str]
    stock_data: StockData
    news_articles: List[NewsArticle]
    youtube_videos: List[YouTubeVideo]
    full_report: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
