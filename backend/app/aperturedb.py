"""
ApertureDB client for caching stock reports.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import logging
from aperturedb.CommonLibrary import create_connector
from aperturedb.Query import Query
import traceback

logger = logging.getLogger(__name__)

class ApertureDBClient:
    """Client for interacting with ApertureDB."""
    
    def __init__(self):
        """Initialize ApertureDB client."""
        self.client = create_connector()
        self.logger = logging.getLogger(__name__)
        self._ensure_collections()
    
    def _ensure_collections(self):
        """Ensure required collections exist."""
        try:
            # Create collection for stock reports if it doesn't exist
            q = Query()
            q.create_collection("stock_reports")
            self.client.execute(q)
        except Exception as e:
            # Collection might already exist
            self.logger.debug(f"Collection creation: {str(e)}")
    
    async def get_cached_report(self, ticker: str, max_age_minutes: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get cached stock report if it exists and is not too old.
        
        Args:
            ticker: Stock ticker symbol
            max_age_minutes: Maximum age of cached data in minutes
            
        Returns:
            Cached report data if found and fresh, None otherwise
        """
        try:
            # Query for the most recent report for this ticker
            q = Query()
            q.find("stock_reports", {"ticker": ticker}).sort("timestamp", ascending=False).limit(1)
            results = self.client.execute(q)
            
            if not results:
                return None
                
            report = results[0]
            
            # Check if report is too old
            report_time = datetime.fromisoformat(report["timestamp"])
            age = datetime.now() - report_time
            
            if age > timedelta(minutes=max_age_minutes):
                return None
                
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting cached report: {str(e)}")
            return None
    
    async def cache_report(self, ticker: str, report_data: Dict[str, Any]) -> None:
        """Cache a stock report in ApertureDB."""
        try:
            self.logger.debug(f"Caching report for ticker: {ticker}")
            
            # Convert datetime objects to ISO format strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            # Convert any datetime objects in the report
            report = convert_datetime(report_data)
            
            # Create query to store report
            query = [{
                "AddEntity": {
                    "class": "stock_reports",
                    "properties": {
                        "ticker": ticker,
                        "report": report,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }]
            
            self.logger.debug("Executing cache query")
            self.client.query(query)
            self.logger.debug("Report cached successfully")
            
        except Exception as e:
            self.logger.error(f"Error caching report: {str(e)}")
            self.logger.debug(traceback.format_exc())
            raise
