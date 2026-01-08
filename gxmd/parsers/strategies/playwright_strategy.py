import asyncio

from playwright.async_api import Browser, async_playwright
from playwright.async_api import TimeoutError

from gxmd.abstracts.fetch_strategy import FetchStrategy
from gxmd.exceptions import GXMTimeoutError


class PlaywrightStrategy(FetchStrategy):
    def __init__(self):
        self.renderer = HtmlRenderer()

    async def fetch(self, url: str) -> str:
        try:
            return await self.renderer.render(url)
        except TimeoutError as e:
            raise GXMTimeoutError(f"Browser timed out while loading: {url}") from e

    async def close(self):
        if self.renderer.is_initialized():
            await self.renderer.close()


class HtmlRenderer:
    _instance = None
    _playwright = None
    _browser: Browser
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def is_initialized(cls):
        return cls._initialized is True

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
            HtmlRenderer._initialized = True
            return self._browser
        return self._browser

    async def render(self, url: str, timeout: int = 15000) -> str:
        """Render any URL using the singleton browser"""
        browser = await self.ensure_browser()
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

        await page.close()
        await context.close()

        return html

    async def close(self):
        """Close when done"""
        if self._initialized:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            HtmlRenderer._initialized = False
            HtmlRenderer._instance = None


browser = HtmlRenderer()
