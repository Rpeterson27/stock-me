from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from .services import StockService
from .models import StockReport
import os
from dotenv import load_dotenv
import asyncio
from typing import AsyncGenerator
import json
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Verify required environment variables
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is required")

app = FastAPI(title="Stock Analysis API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict if deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/report/{ticker}", response_model=StockReport)
async def generate_stock_report(ticker: str):
    """
    Generate a comprehensive stock analysis report including:
    - Basic stock data
    - News articles with sentiment analysis
    - YouTube video insights
    - AI-generated summary and insights
    """
    try:
        async with StockService() as service:
            report = await service.generate_report(ticker)
            return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        logging.error(f"Error generating report for {ticker}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Error generating stock report",
                "error": str(e),
                "ticker": ticker,
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/stream-report/{ticker}")
async def stream_stock_report(ticker: str):
    """
    Stream the stock report generation process, emitting events for:
    - Stock data updates
    - News article processing
    - YouTube video fetching and Agno-powered analysis
    - Final report generation
    
    Events:
    - stock_data: Basic stock information
    - news_article: Each processed news article
    - youtube_video: Each found video
    - youtube_analysis: Agno analysis of video content and captions
    - analysis: Final complete report
    - error: Any errors during processing
    """
    async def event_generator(ticker: str) -> AsyncGenerator[str, None]:
        try:
            # Create a queue for events
            queue = asyncio.Queue()
            
            # Create event handler
            async def handle_event(event_data):
                event = {
                    "event": event_data["type"],
                    "data": json.dumps(event_data["data"]),
                    "id": str(datetime.now().timestamp()),
                    "retry": 3000
                }
                await queue.put(event)
            
            # Initialize service with event handler
            async with StockService(event_handler=handle_event) as service:
                # Start report generation in background
                report_task = asyncio.create_task(service.generate_report(ticker))
                
                # Stream events until report is complete
                while True:
                    try:
                        event = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield event
                        if event["event"] == "analysis" or event["event"] == "error":
                            break
                    except asyncio.TimeoutError:
                        yield {
                            "event": "error",
                            "data": json.dumps({"message": "Timeout waiting for data"}),
                            "id": str(datetime.now().timestamp())
                        }
                        break
                
                # Ensure report generation is complete
                await report_task
                
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
                "id": str(datetime.now().timestamp())
            }
    
    return EventSourceResponse(event_generator(ticker))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
