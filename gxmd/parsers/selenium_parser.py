import posixpath
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from gxmd.abstracts.manga_parser import IMangaParser
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.entities.manga_selector import MangaSelector


# TODO add errors handling like RequestParser
# TODO use chrome if firefox not found
class SeleniumParser(IMangaParser):
    """
    Initializes a SeleniumParser instance with a custom Firefox profile and options. The profile is configured
    to disable image loading and enable downloads, and the browser is set to run in headless mode.
    Args:
        manga_selector (MangaSelector): Configuration for selecting manga elements on a webpage.
        timeout (int): Number of seconds before timing out
    """

    def __init__(self, manga_selector: MangaSelector, manga_url: str, timeout=10):
        print('Selenium Loading ...')
        self.manga_selector = manga_selector
        # Create a Firefox Profile
        profile = FirefoxProfile()

        # Disable image loading
        profile.set_preference('permissions.default.image', 2)

        # Set up Firefox options
        options = Options()
        options.enable_downloads = True
        options.add_argument("-headless")
        options.profile = profile

        # Initialize the WebDriver with the modified options
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, timeout)  # Maximum wait time of 10 seconds

        self._load_page(manga_url)

    def parse_manga_name(self) -> str:
        """
        Parse manga name

        Returns:
            str: manga name.
        """
        selector = self.manga_selector.manga_name
        return self._get_element_content(selector).strip() if selector else self.title

    def parse_chapters_info(self) -> list[MangaChapter]:
        """
        Method to get the list of chapters from the parsed webpage.

        Returns:
            list[MangaChapter]: A list of MangaChapter objects.
        """
        chapters = []
        chapters_web_elements = self._get_elements(self.manga_selector.list_chapters)
        for element in chapters_web_elements:
            element_text = element.get_attribute(self.manga_selector.chapter_name_attr or 'text').strip()
            if self.manga_selector.chapter_name_attr == 'href':
                element_text = posixpath.basename(element_text.rstrip("/"))
            chapter_name = element_text.splitlines()[0].strip()
            chapter_link = element.get_attribute(self.manga_selector.chapter_link_attr or "href").strip()
            chapters.append(MangaChapter(name=chapter_name, link=chapter_link))
        chapters.reverse()
        return chapters

    def parse_chapter_images(self, link: str) -> list[str]:
        """
        Parse chapter images

        Args:
            link (str): link to the chapter

        Returns:
            list[str]: A list of image links.
        """
        self._load_page(link)
        return self._get_elements_attribute(self.manga_selector.chapter_images,
                                            self.manga_selector.image_link_attr)

    def _load_page(self, link: str):
        """
        Navigate to a webpage

        Args:
            link (str): link to the webpage
        """
        self.driver.get(link)

    @property
    def title(self) -> str:
        """
        Returns title of the current loaded webpage.
        """
        return self.driver.title

    def _get_elements_attribute(self, selector: str, attr: str) -> list[str]:
        # Wait until the page is fully loaded
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        urls: [WebElement] = self.driver.find_elements(by=By.CSS_SELECTOR, value=selector)
        return [element.get_attribute(attr).strip() for element in urls]

    def _get_elements(self, selector: str) -> list[WebElement]:
        # Wait until the page is fully loaded
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        elements: list[WebElement] = self.driver.find_elements(by=By.CSS_SELECTOR, value=selector)
        return elements

    def _get_element_content(self, selector: str, attr: str = None) -> str:
        # Wait until the page is fully loaded
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        element: WebElement = self.driver.find_element(by=By.CSS_SELECTOR, value=selector)
        if attr is None:
            return element.text
        return element.get_attribute(attr)

    def export_html(self, wait_selector=None) -> str:
        if wait_selector is not None:
            # Wait until the page is fully loaded
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
        self.driver.find_elements(by=By.CSS_SELECTOR, )
        # Extract and print the page source or perform other automation tasks
        return self.driver.page_source

    def __del__(self):
        # Clean up by closing the browser
        self.driver.quit()
