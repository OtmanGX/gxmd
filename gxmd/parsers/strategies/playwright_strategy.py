import asyncio

from playwright.async_api import Browser, async_playwright, Page, BrowserContext
from playwright.async_api import TimeoutError

from gxmd.abstracts.fetch_strategy import FetchStrategy
from gxmd.config import MAX_TABS
from gxmd.exceptions import GXMTimeoutError


class PlaywrightStrategy(FetchStrategy):
    _instance = None
    _playwright = None
    _browser: Browser
    _initialized = False

    # NEW: global per-strategy concurrency limit (10 "tabs" max)
    _tab_semaphore: asyncio.Semaphore | None = None
    _max_tabs: int = MAX_TABS

    def __new__(cls):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                # Initialize semaphore once (when singleton is created)
                if cls._tab_semaphore is None:
                    cls._tab_semaphore = asyncio.Semaphore(cls._max_tabs)
        return cls._instance

    @classmethod
    def is_initialized(cls):
        return cls._initialized is True

    async def fetch(self, url: str, timeout: int = 15000) -> str:
        """Render any URL using the singleton browser"""
        browser = await self.ensure_browser()
        page: Page | None = None
        context: BrowserContext | None = None

        # Acquire a "tab slot" for the entire render lifecycle
        assert self._tab_semaphore is not None
        async with self._tab_semaphore:
            try:
                # Minimal context: no viewport, no extras
                context = await browser.new_context(
                    viewport=None,
                    java_script_enabled=True,
                    ignore_https_errors=True
                )
                page = await context.new_page()
                # Block all non-HTML/CSS resources upfront
                # await page.route("**/*.{css,woff,woff2,ttf,eot,svg,png,jpg,jpeg,gif,webp}", lambda route: route.abort())

                # Ultra-fast navigation for HTML only
                await page.goto(url, wait_until='commit', timeout=timeout)
                await page.wait_for_load_state()
                await asyncio.sleep(0.9)  # SPA hydration

                # Get raw HTML
                html = await page.content()

                return html
            except TimeoutError as e:
                raise GXMTimeoutError(
                    f"Browser timed out while loading: {url}, The site may be protected by Cloudflare", 504) from e
            except Exception as e:
                raise e
            finally:
                # Only close here (avoid double-close)
                if page is not None:
                    await page.close()
                if context is not None:
                    await context.close()

    async def ensure_browser(self) -> Browser:
        """Lazy init - creates browser only once"""
        if not self._initialized:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True, args=['--no-sandbox',
                                                                                        '--disable-blink-features=AutomationControlled',
                                                                                        '--disable-dev-shm-usage',
                                                                                        '--disable-images',
                                                                                        '--disable-css',
                                                                                        # Native image blocking
                                                                                        '--blink-settings=imagesEnabled=false',
                                                                                        '--disable-background-timer-throttling',
                                                                                        '--disable-backgrounding-occluded-windows',
                                                                                        '--disable-renderer-backgrounding'
                                                                                        ])
            print("✅ Singleton browser created!")
            PlaywrightStrategy._initialized = True
            return self._browser
        return self._browser

    async def close(self):
        """Close when done"""
        if self._initialized:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            PlaywrightStrategy._initialized = False
            PlaywrightStrategy._instance = None
            # optional: keep semaphore, or reset it
            # PlaywrightStrategy._tab_semaphore = asyncio.Semaphore(self._max_tabs)


browser = PlaywrightStrategy()
