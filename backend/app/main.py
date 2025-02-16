from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services import StockService
from .models import StockReport
import os
from dotenv import load_dotenv

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
