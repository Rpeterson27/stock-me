import asyncio
import pytest
from datetime import datetime, timedelta
from backend.app.cache import CacheService
import json

@pytest.mark.asyncio
async def test_cache_operations():
    """Test basic cache operations with ApertureDB."""
    cache = CacheService()
    
    # Test data
    ticker = "AAPL"
    current_time = datetime.fromisoformat("2025-02-16T12:20:40-08:00")
    cache.current_time = current_time  # Set current time for testing
    test_data = {
        "price": 150.25,
        "volume": 1000000,
        "timestamp": current_time.isoformat()
    }
    
    try:
        # Test setting data
        print("\n1. Setting data...")
        await cache.set("stock_data", ticker, test_data)
        print("✅ Successfully cached data")
        
        # Wait a moment to ensure the data is set
        await asyncio.sleep(0.5)
        
        # Test retrieving data
        print("\n2. Retrieving data...")
        retrieved_data = await cache.get("stock_data", ticker)
        print(f"Retrieved data: {json.dumps(retrieved_data, indent=2)}")
        
        if retrieved_data is None:
            print("❌ Retrieved data is None")
            print(f"Original test data: {json.dumps(test_data, indent=2)}")
            print(f"Current time: {datetime.now().isoformat()}")
        else:
            print("✅ Retrieved data successfully")
        
        assert retrieved_data is not None, "Retrieved data should not be None"
        assert retrieved_data["price"] == test_data["price"]
        print("✅ Successfully retrieved cached data")
        
        # Test expired data
        print("\n3. Testing cache expiration (simulated)...")
        # Force expiration by modifying timestamp
        expired_time = current_time - timedelta(minutes=11)
        expired_data = {
            "price": 148.25,
            "volume": 900000,
            "timestamp": expired_time.isoformat()
        }
        await cache.set("stock_data", "AAPL_EXPIRED", expired_data)  # Use a different ticker
        
        # Get expired data
        retrieved_expired = await cache.get("stock_data", "AAPL_EXPIRED")
        assert retrieved_expired is None, "Expired data should be None"
        print("✅ Cache expiration working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise e
    finally:
        # Clean up
        print("\n4. Cleaning up...")
        clear_query = [{
            "DeleteEntity": {
                "with_class": "stock_data",
                "constraints": {}
            }
        }]
        print(f"Clear Query: {json.dumps(clear_query, indent=2)}")
        clear_result = cache.client.query(clear_query)
        print(f"Clear Result: {json.dumps(clear_result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_cache_operations())
