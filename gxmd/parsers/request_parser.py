import requests
import posixpath
from bs4 import BeautifulSoup
from requests import Response
from gxmd.abstracts.manga_parser import IMangaParser
from gxmd.constants import USER_AGENT
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.entities.manga_selector import MangaSelector
from gxmd.parsers.exceptions import *
from gxmd.utils import combine_whitespaces


class RequestParser(IMangaParser):
    soup: BeautifulSoup = None

    def __init__(self, manga_selector: MangaSelector, manga_url: str, timeout=10):
        self.manga_selector = manga_selector
        self.timeout = timeout
        self._load_page(manga_url)

    @property
    def title(self) -> str:
        """
        Returns title of the current loaded webpage.
        """
        return self.soup.title.string.strip()

    def parse_manga_name(self) -> str:
        """
        Parse manga name

        Returns:
            str: manga name.
        """
        selector = self.manga_selector.manga_name
        if selector is not None:
            element = self.soup.select_one(selector)
            if element is None:
                raise ParseMangaNameException(selector)
            return element.text.strip()
        return self.title

    def parse_chapters_info(self) -> list[MangaChapter]:
        """
        Method to get the list of chapters from the parsed webpage.

        Returns:
            list[MangaChapter]: A list of MangaChapter objects.
        """
        chapters = []
        selector: str = self.manga_selector.list_chapters
        chapters_web_elements = self.soup.select(selector)
        if chapters_web_elements is None or len(chapters_web_elements) == 0:
            raise ParseChaptersListException(selector)
        for i, element in enumerate(chapters_web_elements):
            chapter_name_attr = self.manga_selector.chapter_name_attr
            if chapter_name_attr:
                element_text = element.get(chapter_name_attr)
                if element_text is None:
                    raise ParseChapterNameException(chapter_name_attr)
            else:
                element_text = combine_whitespaces(tuple(element.stripped_strings)[0])
            if self.manga_selector.chapter_name_attr == 'href':
                element_text = posixpath.basename(element_text.strip().rstrip("/"))
            chapter_name = element_text.strip().splitlines()[0].strip()
            if chapter_name.lower() == "chapter":
                chapter_name = chapter_name + str(len(chapters_web_elements)-i)
            chapter_link_attr = self.manga_selector.chapter_link_attr or "href"
            chapter_link = element.get(chapter_link_attr).strip()
            if chapter_link is None:
                raise ParseChapterLinkException(chapter_link_attr)
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
        image_elements = self.soup.select(self.manga_selector.chapter_images)
        return [element.get(self.manga_selector.image_link_attr) for element in image_elements]

    def _load_page(self, link: str):
        """
        Navigate to a webpage

        Args:
            link (str): link to the webpage
        """
        res: Response = requests.get(link, headers={'User-Agent': USER_AGENT}, timeout=self.timeout)
        self.soup = BeautifulSoup(res.content, 'html.parser')

    def export_html(self, wait_selector=None) -> str:
        return self.soup.decode()
