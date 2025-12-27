from abc import ABC, abstractmethod

from gxmd.entities.manga_chapter import MangaChapter


class IMangaParser(ABC):
    @abstractmethod
    def _load_page(self, link: str):
        """
        Navigate to a webpage

        Args:
            link (str): link to the webpage
        """
        pass

    @abstractmethod
    async def parse_manga_info(self) -> tuple[str, list[MangaChapter]]:
        """
        Parse manga info
        """
        pass

    @abstractmethod
    async def parse_chapter_images(self, link: str) -> list[str]:
        """
        Parse chapter images

        Args:
            link (str): link to the chapter

        Returns:
            list[str]: A list of image links.
        """
        pass

    @abstractmethod
    async def close(self):
        pass
