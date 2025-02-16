"""
ApertureDB-based caching service for stock reports.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import traceback
from aperturedb.CommonLibrary import create_connector
import pytz
import pandas as pd

logger = logging.getLogger(__name__)

class CacheService:
    """Service for caching stock data and reports using ApertureDB."""
    
    def __init__(self):
        """Initialize the cache service."""
        self.client = create_connector()
        self.logger = logging.getLogger(__name__)
        self.current_time = datetime.fromisoformat("2025-02-16T12:20:40-08:00")
        self.logger.debug(f"Initialized with current_time: {self.current_time} (tzinfo: {self.current_time.tzinfo})")
        self._ensure_collections()
    
    def _ensure_collections(self):
        """Ensure required collections exist."""
        try:
            # Create collections if they don't exist
            collections = ["stock_data", "news_articles", "youtube_videos", "analysis"]
            for collection in collections:
                try:
                    self.client.query([{
                        "CreateClass": {
                            "class": collection,
                            "properties": {
                                "ticker": {
                                    "type": "string"
                                },
                                "timestamp": {
                                    "type": "string"
                                },
                                "data": {
                                    "type": "json"
                                }
                            }
                        }
                    }])
                except Exception as e:
                    # Ignore error if collection already exists
                    if "already exists" not in str(e):
                        raise
            
            self.logger.debug("✅ Collections created successfully")
        except Exception as e:
            self.logger.debug(f"Collection creation: {str(e)}")
    
    async def get(self, collection: str, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a ticker from the cache.
        
        Args:
            collection: Collection name (stock_data, news_articles, youtube_videos, analysis)
            ticker: Stock ticker symbol
            
        Returns:
            Data if found and not expired, None otherwise
        """
        try:
            self.logger.debug("=== START GET DEBUG ===")
            self.logger.debug(f"Getting data for {ticker} from {collection}")
            
            # Query ApertureDB
            get_query = [{
                "FindEntity": {
                    "with_class": collection,
                    "constraints": {
                        "ticker": ["==", ticker]
                    },
                    "results": {
                        "list": ["ticker", "timestamp", "data"]
                    }
                }
            }]
            self.logger.debug(f"Get Query: {json.dumps(get_query, indent=2)}")
            get_result = self.client.query(get_query)
            self.logger.debug(f"Get Result: {json.dumps(get_result, indent=2)}")
            
            # Check if data exists
            if not get_result or not get_result[0] or not get_result[0][0].get("FindEntity"):
                self.logger.debug("No data found")
                return None
                
            # Get the entities
            find_entity = get_result[0][0]["FindEntity"]
            entities = find_entity.get("entities", [])
            if not entities:
                self.logger.debug("No entities found")
                return None
                
            # Get the first result (should be most recent)
            result = entities[0]
            if not result:
                self.logger.debug("Empty result")
                return None
                
            # Return the data
            data = result.get("data")
            if not data:
                self.logger.debug("No data found in result")
                return None
                
            # Parse timestamp
            timestamp_str = data.get("timestamp")
            if not timestamp_str:
                self.logger.debug("No timestamp found in data")
                return None
                
            timestamp = datetime.fromisoformat(timestamp_str)
            self.logger.debug(f"Data timestamp: {timestamp.isoformat()}")
            self.logger.debug(f"Current time: {self.current_time.isoformat()}")
            self.logger.debug(f"Time difference: {(self.current_time - timestamp).total_seconds() / 60} minutes")
            
            # Check if data is expired (older than 10 minutes)
            if (self.current_time - timestamp) > timedelta(minutes=10):
                self.logger.debug(f"Data expired: {timestamp_str}")
                return None
                
            self.logger.debug(f"Found data: {json.dumps(data, indent=2)}")
            self.logger.debug("=== END GET DEBUG ===")
            return data
            
        except Exception as e:
            self.logger.error(f"Error getting cached data: {str(e)}")
            return None
            
    async def set(self, collection: str, ticker: str, data: Dict[str, Any]) -> None:
        """
        Set data for a ticker in the cache.
        
        Args:
            collection: Collection name (stock_data, news_articles, youtube_videos, analysis)
            ticker: Stock ticker symbol
            data: Data to cache
        """
        try:
            self.logger.debug(f"=== START CACHE SET ===")
            self.logger.debug(f"Collection: {collection}")
            self.logger.debug(f"Key: {ticker}")
            
            # Convert Timestamp objects to ISO format strings
            def convert_timestamps(obj):
                self.logger.debug(f"Converting object type: {type(obj)}")
                if hasattr(obj, 'to_dict'):
                    self.logger.debug("Object has to_dict method")
                    try:
                        dict_data = obj.to_dict()
                        self.logger.debug(f"Dict keys: {list(dict_data.keys())}")
                        result = {}
                        for k, v in dict_data.items():
                            self.logger.debug(f"Processing key type: {type(k)}, value type: {type(v)}")
                            key_str = str(k) if hasattr(k, 'isoformat') else k
                            result[key_str] = convert_timestamps(v)
                        return result
                    except Exception as e:
                        self.logger.error(f"Error converting to_dict: {str(e)}")
                        raise
                elif hasattr(obj, 'isoformat'):
                    self.logger.debug("Converting datetime-like object to ISO format")
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    self.logger.debug("Converting dictionary")
                    try:
                        result = {}
                        for k, v in obj.items():
                            self.logger.debug(f"Dict key type: {type(k)}, value type: {type(v)}")
                            key_str = str(k) if hasattr(k, 'isoformat') else k
                            result[key_str] = convert_timestamps(v)
                        return result
                    except Exception as e:
                        self.logger.error(f"Error converting dict: {str(e)}")
                        raise
                return obj
            
            self.logger.debug("Converting data timestamps")
            data = convert_timestamps(data)
            
            # Create document with TTL
            expires_at = self.current_time + timedelta(minutes=10)
            document = {
                "ticker": ticker,
                "data": data,
                "timestamp": expires_at.isoformat()
            }
            
            self.logger.debug("Preparing to insert into ApertureDB")
            try:
                self.logger.debug("Converting document to JSON")
                json_str = json.dumps(document)
                self.logger.debug("JSON conversion successful")
            except Exception as e:
                self.logger.error(f"Error converting to JSON: {str(e)}")
                self.logger.debug(f"Document structure: {type(document)}")
                for k, v in document.items():
                    self.logger.debug(f"Key: {k}, Value type: {type(v)}")
                raise
            
            # Insert into collection
            self.logger.debug(f"Inserting into collection: {collection}")
            set_query = [{
                "AddEntity": {
                    "class": collection,
                    "properties": document
                }
            }]
            self.client.query(set_query)
            self.logger.debug(f"Cache set successfully for {collection}/{ticker}")
            self.logger.debug("=== END CACHE SET ===")
            
        except Exception as e:
            self.logger.error(f"Error setting cache: {str(e)}")
            self.logger.debug(f"Collection: {collection}, Key: {ticker}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
