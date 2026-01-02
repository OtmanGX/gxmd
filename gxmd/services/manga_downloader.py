import os
import time

from aiohttp.web_exceptions import HTTPRequestTimeout
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

from gxmd.config import USER_AGENT
from gxmd.entities.manga import Manga
from gxmd.parsers.request_parser import RequestParser
from gxmd.services.download_manager import DownloadManager
from gxmd.services.exporter import RawExporter, ExporterBase


class MangaDownloader:
    """
    A class to manage the downloading of manga chapters from supported websites.

    Attributes:
        manga (Manga): manga dataclass object.
        download_manager (DownloadManager): Manages the downloading of files.
    """
    manga: Manga = None

    def __init__(self, manga: Manga, download_manager: DownloadManager, exporter_class=RawExporter):
        """
        Initializes the MangaDownloader object with manga link, selector, and download manager.

        Args:
            manga (Manga): manga instance.
            download_manager (DownloadManager): The download manager instance for handling downloads.
            exporter_class (Class): The exporter class.
        """
        self.manga = manga
        self.download_manager = download_manager
        self.exporter_class = exporter_class

    @property
    def chapters(self):
        return self.manga.chapters

    def list_chapters(self):
        """
        Prints the chapters in two columns, showing a maximum of 8 chapters followed by '...' and the last chapter if
        there are more than 10 chapters.
        """
        num_chapters = len(self.chapters)
        if num_chapters > 10:
            # Select the first 8 and the last chapter to display
            selected_chapters = self.chapters[:8] + ['...'] + [self.chapters[-1]]
        else:
            selected_chapters = self.chapters

        # Calculate the number of rows for printing in two columns
        num_rows = (len(selected_chapters) + 1) // 2

        # Print chapters in two columns
        for i in range(num_rows):
            # Check if there is a corresponding chapter in the second column
            if i + num_rows < len(selected_chapters):
                if selected_chapters[i + num_rows] == '...':
                    print(f"{i + 1}. {selected_chapters[i].name:30} ...")
                else:
                    # Adjust the index for the second column
                    second_column_index = num_chapters if selected_chapters[i + num_rows] == self.chapters[
                        -1] else i + num_rows + 1
                    print(
                        f"{i + 1}. {selected_chapters[i].name:30} {second_column_index}. "
                        f"{selected_chapters[i + num_rows].name}"
                    )
            else:
                # Adjust the index for the last item if it's the very last chapter
                last_index = num_chapters if selected_chapters[i] == self.chapters[-1] else i + 1
                print(f"{last_index}. {selected_chapters[i].name}")

    async def download_chapters(self, start: int = None, end: int = None, job: dict = None):
        """
        Downloads the specified range of chapters.

        Args:
            start (int, optional): Starting index of chapters to download. Defaults to 0.
            end (int, optional): Ending index of chapters to download. Defaults to the last chapter.
            job (dict, optional): Job details.
        """
        exporter = self.exporter_class(
            os.path.join(self.download_manager.downloads_directory, self.manga.title)
        )
        start = start - 1 if start else 0
        end = end or len(self.chapters)
        for i in range(start, end):
            await self._download_chapter(i, exporter)
            if job:
                job['progress'] += 1
        exporter.close()
        await self.download_manager.close()

        time.sleep(0.2)
        print("\nDownload completed ^^")

    async def download_chapter(self, index: int):
        """
        method to download a specific chapter by index.

        Args:
            index (int): Index of the chapter in the list.
        """
        exporter = self.exporter_class(
            os.path.join(self.download_manager.downloads_directory, self.manga.title)
        )
        await self._download_chapter(index - 1, exporter)
        exporter.close()
        await self.download_manager.close()

    async def _download_chapter(self, index: int, exporter: ExporterBase):
        """
        Private method to download a specific chapter by index.

        Args:
            index (int): Index of the chapter in the list.
        """
        chapter = self.chapters[index]
        images_to_download = await RequestParser().parse_chapter_images(chapter.link)

        start_message = f"Downloading {chapter.name.capitalize()}"
        await self.download_manager.download_files_async(
            exporter,
            links=images_to_download,
            headers={'Referer': chapter.link, 'User-Agent': USER_AGENT, 'Accept-Encoding': 'identity'},
            path=chapter.name,
            start_message=start_message,
        )

    @classmethod
    async def load_manga(cls, manga_link: str, download_manager: DownloadManager, exporter_class=RawExporter):
        """
        Class method to load manga configuration and return an instance of MangaDownloader.

        Args:
            manga_link (str): URL to the manga's main page.
            download_manager (DownloadManager): The download manager instance.
            exporter_class (Class): the exporter class.

        Returns:
            MangaDownloader: An instance of MangaDownloader.

        Raises:
            Exception: If the website is not supported.
        """
        manga = await cls.load_manga_info(manga_link)
        return cls(manga, download_manager, exporter_class)

    @classmethod
    async def load_manga_from_info(cls, manga: Manga, download_manager: DownloadManager, exporter_class=RawExporter):
        """
        Class method to load manga configuration and return an instance of MangaDownloader.

        Args:
            manga (Manga): manga instance.
            download_manager (DownloadManager): The download manager instance.
            exporter_class (Class): the exporter class.

        Returns:
            MangaDownloader: An instance of MangaDownloader.

        Raises:
            Exception: If the website is not supported.
        """

        return cls(manga, download_manager, exporter_class)

    @staticmethod
    async def load_manga_info(manga_link: str):
        """
        Static method to load manga information from a given link.

        The method retrieves the appropriate parser based on the manga link, processes
        the manga information to extract its title and chapters, and then constructs
        and returns a Manga object populated with the retrieved details.

        Args:
            manga_link (str): The URL of the manga to load information from.

        Returns:
            Manga: An object containing the title, URL, and list of chapters.

        Raises:
            Exception: If the parser fails to retrieve or process the manga information.
        """
        try:
            title, chapters = await RequestParser().parse_manga_info(manga_link)
        except (PlaywrightTimeoutError, HTTPRequestTimeout):
            raise TimeoutError("Timeout Error")
        return Manga(title=title, url=manga_link, chapters=chapters)
