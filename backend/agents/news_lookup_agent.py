from typing import List, Dict, Any
import logging
from .browser_context import BrowserContext
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

async def fetch_news_links(ticker: str) -> List[Dict[str, Any]]:
    """
    Fetch news links for a given stock ticker from Yahoo Finance.
    """
    try:
        # Get browser context instance
        browser_ctx = await BrowserContext.get_instance()
        
        async with browser_ctx.get_page() as page:
            # Navigate to Yahoo Finance news page
            url = f"https://finance.yahoo.com/quote/{ticker}/news"
            await page.goto(url, wait_until='networkidle')
            
            # Wait for news articles to load
            await page.wait_for_selector('li[data-test="ContentList"]', timeout=10000)
            
            # Extract news articles using Playwright's evaluate
            articles = await page.evaluate("""
                () => {
                    const articles = [];
                    document.querySelectorAll('li[data-test="ContentList"]').forEach(article => {
                        const titleEl = article.querySelector('a');
                        const summaryEl = article.querySelector('p');
                        const sourceEl = article.querySelector('div[data-test="ContentHeader"] span');
                        
                        if (titleEl) {
                            articles.push({
                                headline: titleEl.textContent.trim(),
                                url: titleEl.href,
                                summary: summaryEl ? summaryEl.textContent.trim() : '',
                                source: sourceEl ? sourceEl.textContent.trim() : 'Yahoo Finance'
                            });
                        }
                    });
                    return articles;
                }
            """)
            
            # Process articles and add sentiment
            processed_articles = []
            for article in articles[:10]:  # Process top 10 articles
                # Simple sentiment analysis
                text = (article['headline'] + ' ' + article['summary']).lower()
                sentiment = analyze_sentiment(text)
                
                processed_articles.append({
                    "headline": article['headline'],
                    "summary": article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary'],
                    "url": article['url'],
                    "source": article['source'],
                    "published_at": datetime.now().isoformat(),
                    "sentiment": sentiment
                })
            
            return processed_articles
            
    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {str(e)}")
        return []

def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    positive_words = {'rise', 'gain', 'up', 'growth', 'positive', 'bullish', 'surge', 'jump', 'strong', 'beat'}
    negative_words = {'fall', 'drop', 'down', 'decline', 'negative', 'bearish', 'plunge', 'weak', 'miss', 'loss'}
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    return 'neutral'

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
