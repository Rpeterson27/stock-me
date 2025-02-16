import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from playwright.async_api import async_playwright, Browser, Page, BrowserContext as PlaywrightContext
from agentql import wrap_async
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BrowserContext:
    _instance = None
    _browser: Browser = None
    _context: PlaywrightContext = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_instance(cls) -> 'BrowserContext':
        """Get singleton instance of BrowserContext"""
        if not cls._instance:
            async with cls._lock:
                if not cls._instance:
                    logger.info("Creating new BrowserContext instance")
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance
    
    async def _initialize(self):
        """Initialize browser instance"""
        if not self._browser:
            try:
                logger.info("Starting Playwright and launching browser")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                logger.info("Creating browser context with custom viewport and user agent")
                self._context = await self._browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                logger.info("Browser initialization complete")
            except Exception as e:
                logger.error(f"Error during browser initialization: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                raise
    
    @asynccontextmanager
    async def get_page(self) -> AsyncGenerator[Page, None]:
        """
        Get a new page with AgentQL initialized.
        Usage:
            async with browser_ctx.get_page() as page:
                # Use page here
        """
        if not self._context:
            logger.info("No browser context found, initializing")
            await self._initialize()
            
        logger.info("Creating new page")
        page = await self._context.new_page()
        wrapped_page = None
        try:
            # Set longer timeouts for stability
            logger.debug("Setting page timeouts")
            page.set_default_timeout(30000)  # 30 seconds
            page.set_default_navigation_timeout(30000)
            
            # Initialize AgentQL by wrapping the page
            logger.debug("Wrapping page with AgentQL")
            try:
                # Use wrap_async for async code
                wrapped_page = await wrap_async(page)
                logger.info("Successfully wrapped page with AgentQL")
                yield wrapped_page
            except Exception as e:
                logger.error(f"Error wrapping page with AgentQL: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                raise
        finally:
            try:
                # Small delay before closing to ensure operations complete
                logger.debug("Waiting before closing page")
                await asyncio.sleep(0.5)
                
                if wrapped_page:
                    logger.info("Closing wrapped page")
                    await wrapped_page.close()
                elif not page.is_closed():
                    logger.info("Closing unwrapped page")
                    await page.close()
            except Exception as e:
                logger.error(f"Error closing page: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
    
    @classmethod
    async def close(cls):
        """Close browser and cleanup"""
        if cls._instance:
            try:
                if cls._instance._context:
                    logger.info("Closing browser context")
                    await cls._instance._context.close()
                if cls._instance._browser:
                    logger.info("Closing browser")
                    await cls._instance._browser.close()
                if hasattr(cls._instance, '_playwright'):
                    logger.info("Stopping Playwright")
                    await cls._instance._playwright.stop()
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
            finally:
                logger.info("Resetting browser context instance")
                if hasattr(cls._instance, '_playwright'):
                    cls._instance._playwright = None
                cls._instance._context = None
                cls._instance._browser = None
                cls._instance = None
