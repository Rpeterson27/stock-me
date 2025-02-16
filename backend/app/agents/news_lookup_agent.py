from datetime import datetime
from typing import List, Dict, Any
import asyncio
from .browser_context import BrowserContext
from playwright._impl._errors import TimeoutError, Error, TargetClosedError
import logging
import traceback

logger = logging.getLogger(__name__)

async def fetch_news_links(query: str, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Fetches financial news links for a given query, prioritizing accessible sources.
    
    Args:
        query: Stock ticker or company name
        max_retries: Number of retries on failure
        
    Returns:
        List of news article information
    """
    logger.info(f"Fetching news for query: {query}")
    browser_ctx = await BrowserContext.get_instance()
    
    async with browser_ctx.get_page() as page:
        results = None
        retry_count = 0
        
        while retry_count < max_retries and not results:
            try:
                # Target Yahoo Finance first
                yahoo_url = f"https://finance.yahoo.com/quote/{query}/news"
                logger.info(f"Attempting to navigate to Yahoo Finance: {yahoo_url}")
                await page.goto(yahoo_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)  # Small delay to ensure content loads
                
                # Extract news links from Yahoo Finance using specific selectors
                try:
                    logger.debug("Querying Yahoo Finance with AgentQL")
                    results = await page.query_data("""
                    {
                        news_section(must be div with id="marketsNews") {
                            articles[] {
                                title(must be h3 text)
                                url(must be a href)
                                description(must be p text)
                                source(must be span with class="caas-author")
                                time(must be span with class="caas-timestamp")
                            }
                        }
                    }
                    """)
                    if results and results.get('news_section', {}).get('articles'):
                        logger.info("Successfully retrieved articles from Yahoo Finance")
                except (Error, TargetClosedError) as e:
                    logger.error(f"Error querying Yahoo Finance: {str(e)}")
                    logger.error(f"Stack trace: {traceback.format_exc()}")
                    results = None
                
                # If Yahoo fails, try Reuters
                if not results or not results.get('news_section', {}).get('articles'):
                    logger.info("Yahoo Finance failed, trying Reuters...")
                    reuters_url = f"https://www.reuters.com/markets/companies/{query}.O"
                    logger.info(f"Attempting to navigate to Reuters: {reuters_url}")
                    await page.goto(reuters_url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(2)  # Small delay to ensure content loads
                    
                    try:
                        logger.debug("Querying Reuters with AgentQL")
                        results = await page.query_data("""
                        {
                            articles[] {
                                title(must be h3 text)
                                url(must be a href)
                                description(must be p text)
                                source(must be div with class="article-info" text)
                                time(must be time text)
                            }
                        }
                        """)
                        if results and results.get('articles'):
                            logger.info("Successfully retrieved articles from Reuters")
                    except (Error, TargetClosedError) as e:
                        logger.error(f"Error querying Reuters: {str(e)}")
                        logger.error(f"Stack trace: {traceback.format_exc()}")
                        results = None
            
            except (TimeoutError, TargetClosedError) as e:
                logger.error(f"Navigation error on attempt {retry_count + 1}: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                retry_count += 1
                await asyncio.sleep(1)  # Wait before retry
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {retry_count + 1}: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                retry_count += 1
                await asyncio.sleep(1)  # Wait before retry
                continue
        
        # Process results
        articles = []
        if results:
            if results.get('news_section', {}).get('articles'):  # Yahoo Finance format
                logger.info(f"Processing {len(results['news_section']['articles'])} articles from Yahoo Finance")
                for article in results['news_section']['articles']:
                    # Basic sentiment inference from title and description
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    sentiment = 'neutral'
                    
                    # Simple keyword-based sentiment analysis
                    positive_words = {'rise', 'gain', 'up', 'growth', 'positive', 'bullish', 'surge', 'jump', 'strong', 'beat'}
                    negative_words = {'fall', 'drop', 'down', 'decline', 'negative', 'bearish', 'plunge', 'weak', 'miss', 'loss'}
                    
                    text = title + ' ' + description
                    pos_count = sum(1 for word in positive_words if word in text)
                    neg_count = sum(1 for word in negative_words if word in text)
                    
                    if pos_count > neg_count:
                        sentiment = 'positive'
                    elif neg_count > pos_count:
                        sentiment = 'negative'
                    
                    articles.append({
                        "headline": article.get('title', ''),
                        "summary": article.get('description', '')[:200] + "...",
                        "url": article.get('url', ''),
                        "source": article.get('source', 'Yahoo Finance'),
                        "published_at": datetime.now().isoformat(),  # Store as ISO format string
                        "sentiment": sentiment
                    })
            elif results.get('articles'):  # Reuters format
                logger.info(f"Processing {len(results['articles'])} articles from Reuters")
                for article in results['articles']:
                    # Convert relative Reuters URLs to absolute
                    url = article.get('url', '')
                    if url.startswith('/'):
                        url = f"https://www.reuters.com{url}"
                    
                    # Basic sentiment inference from title and description
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    sentiment = 'neutral'
                    
                    # Simple keyword-based sentiment analysis
                    positive_words = {'rise', 'gain', 'up', 'growth', 'positive', 'bullish', 'surge', 'jump', 'strong', 'beat'}
                    negative_words = {'fall', 'drop', 'down', 'decline', 'negative', 'bearish', 'plunge', 'weak', 'miss', 'loss'}
                    
                    text = title + ' ' + description
                    pos_count = sum(1 for word in positive_words if word in text)
                    neg_count = sum(1 for word in negative_words if word in text)
                    
                    if pos_count > neg_count:
                        sentiment = 'positive'
                    elif neg_count > pos_count:
                        sentiment = 'negative'
                        
                    articles.append({
                        "headline": article.get('title', ''),
                        "summary": article.get('description', '')[:200] + "...",
                        "url": url,
                        "source": "Reuters",
                        "published_at": datetime.now().isoformat(),  # Store as ISO format string
                        "sentiment": sentiment
                    })
        
        logger.info(f"Returning {len(articles)} articles")
        return articles

if __name__ == "__main__":
    async def test():
        stock_ticker = "AAPL"
        news_links = await fetch_news_links(stock_ticker)
        if not news_links:
            print(f"No news found for {stock_ticker}")
        else:
            for article in news_links:
                print(f"\nHeadline: {article['headline']}")
                print(f"Summary: {article['summary']}")
                print(f"URL: {article['url']}")
                print(f"Source: {article['source']}")
                print(f"Published: {article['published_at']}")
                print(f"Sentiment: {article['sentiment']}")
                print("-" * 80)
    
    asyncio.run(test())
