from abc import ABC, abstractmethod
from gxmd.entities.manga_chapter import MangaChapter


class IMangaParser(ABC):

    @abstractmethod
    def title(self) -> str:
        """
        Returns title of the current loaded webpage.
        """
        pass

    @abstractmethod
    def parse_manga_name(self) -> str:
        """
        Parse manga name

        Returns:
            str: manga name.
        """
        pass

    @abstractmethod
    def parse_chapters_info(self) -> list[MangaChapter]:
        """
        Method to get the list of chapters from the parsed webpage.

        Returns:
            list[MangaChapter]: A list of MangaChapter objects.
        """
        pass

    @abstractmethod
    def parse_chapter_images(self, link: str) -> list[str]:
        """
        Parse chapter images

        Args:
            link (str): link to the chapter

        Returns:
            list[str]: A list of image links.
        """
        pass

    @abstractmethod
    def _load_page(self, link: str):
        """
        Navigate to a webpage

        Args:
            link (str): link to the webpage
        """
        pass

    @abstractmethod
    def export_html(self, wait_selector=None) -> str:
        pass
