from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re
import logging
from .browser_context import BrowserContext

logger = logging.getLogger(__name__)

def standardize_date(date_str: str) -> Optional[str]:
    """
    Converts various date formats to ISO format (YYYY-MM-DD).
    Handles common formats like:
    - "2h ago", "5d ago"
    - "Feb 15, 2025"
    - "2025-02-15"
    - "15/02/2025"
    """
    if not date_str:
        return None
        
    # Clean the input
    date_str = date_str.strip().lower()
    
    # Handle relative dates
    if "ago" in date_str:
        now = datetime.now()
        if "h" in date_str:  # hours ago
            hours = int(re.search(r'\d+', date_str).group())
            return (now - timedelta(hours=hours)).isoformat()
        elif "d" in date_str:  # days ago
            days = int(re.search(r'\d+', date_str).group())
            return (now - timedelta(days=days)).isoformat()
            
    try:
        # Try parsing with different formats
        for fmt in ["%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
    except Exception:
        return None
    
    return None

def clean_text(text: str) -> str:
    """
    Cleans and normalizes text content.
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common noise patterns
    patterns_to_remove = [
        r'Advertisement\s*',
        r'Subscribe now.*',
        r'Sign up.*',
        r'Read more.*',
        r'©\s*\d{4}.*',  # Copyright notices
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

async def is_paywall_detected(page) -> bool:
    """
    Detects if an article is behind a paywall using multiple detection methods.
    """
    paywall_indicators = [
        "//div[contains(text(), 'Subscribe to read')]",
        "//div[contains(text(), 'Premium content')]",
        "//div[contains(text(), 'Subscriber-only')]",
        "//div[contains(@class, 'paywall')]",
        "//div[contains(@class, 'subscribe')]",
    ]
    
    try:
        for indicator in paywall_indicators:
            if await page.locator(indicator).count() > 0:
                return True
                
        # Check for login/subscription buttons
        login_buttons = await page.locator("button:has-text('Subscribe'), button:has-text('Sign in')").count()
        if login_buttons > 0:
            # Verify if main content is hidden/truncated
            article_text = await page.locator("article").inner_text()
            if len(article_text) < 500:  # Typical paywall preview length
                return True
    except Exception as e:
        logger.error(f"Error in paywall detection: {str(e)}")
        
    return False

async def scrape_article_content(url: str) -> Dict[str, Any]:
    """
    Extracts full article content using a hybrid approach:
    1. AgentQL for smart content detection and structure analysis
    2. Playwright selectors as fallback
    """
    logger.info(f"Scraping article content from: {url}")
    browser_ctx = await BrowserContext.get_instance()
    
    async with browser_ctx.get_page() as page:
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Check for paywall
            if await is_paywall_detected(page):
                logger.warning(f"Paywall detected for {url}")
                return {
                    "url": url,
                    "is_paywalled": True,
                    "content": None,
                    "error": "Article is behind a paywall"
                }
            
            # Try AgentQL first for structured content extraction
            try:
                article_data = await page.query_data("""
                {
                    article {
                        headline(must be h1 text)
                        author(must be span or a containing "By" or "Author")
                        date(must be time tag or span containing date)
                        content(must be article text or div with class containing "article" or "content")
                    }
                }
                """)
                
                if article_data and article_data.get('article'):
                    content = clean_text(article_data['article'].get('content', ''))
                    return {
                        "url": url,
                        "is_paywalled": False,
                        "headline": article_data['article'].get('headline'),
                        "author": article_data['article'].get('author'),
                        "date": standardize_date(article_data['article'].get('date')),
                        "content": content,
                        "content_length": len(content) if content else 0
                    }
            
            except Exception as e:
                logger.warning(f"AgentQL extraction failed, falling back to selectors: {str(e)}")
            
            # Fallback to traditional selectors
            content_selectors = [
                "article",
                "div[class*='article-content']",
                "div[class*='story-content']",
                "div[class*='post-content']",
                "div[itemprop='articleBody']"
            ]
            
            for selector in content_selectors:
                content_el = await page.locator(selector).first
                if content_el:
                    content = clean_text(await content_el.inner_text())
                    if len(content) > 200:  # Minimum content length threshold
                        return {
                            "url": url,
                            "is_paywalled": False,
                            "content": content,
                            "content_length": len(content)
                        }
            
            return {
                "url": url,
                "is_paywalled": False,
                "error": "Could not extract content with any method",
                "content": None
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "is_paywalled": False,
                "error": str(e),
                "content": None
            }

if __name__ == "__main__":
    # Test with a known article URL
    test_url = "https://finance.yahoo.com/news/apple-inc-aapl-among-best-173037368.html"
    import asyncio
    article_data = asyncio.run(scrape_article_content(test_url))
    
    if article_data.get('error'):
        print(f"Error: {article_data['message']}")
    else:
        print("Headline:", article_data['headline'])
        print("Author:", article_data['author'])
        print("Date:", article_data['date'])
        print("\nContent Preview:", article_data['content'][:500] + "...")
