import asyncio

from playwright.async_api import Browser, async_playwright

from gxmd.abstracts.fetch_strategy import FetchStrategy


class PlaywrightStrategy(FetchStrategy):
    def __init__(self):
        self.renderer = HtmlRenderer()

    async def fetch(self, url: str) -> str:
        return await self.renderer.render(url)

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
                                                                                        # Native image blocking
                                                                                        '--blink-settings=imagesEnabled=false', ])
            print("✅ Singleton browser created!")
            HtmlRenderer._initialized = True
            return self._browser
        return self._browser

    async def render(self, url: str, timeout: int = 30000) -> str:
        """Render any URL using the singleton browser"""
        browser = await self.ensure_browser()
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle', timeout=timeout)
        await page.wait_for_load_state()
        await asyncio.sleep(1)  # SPA hydration
        content = await page.content()
        await page.close()
        return content

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
