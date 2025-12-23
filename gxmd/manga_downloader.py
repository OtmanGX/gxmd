import os
import time
from gxmd.abstracts.manga_parser import IMangaParser
from gxmd.constants import USER_AGENT
from gxmd.download_manager import DownloadManager
from gxmd.parsers.request_parser import RequestParser
from gxmd.parsers.selenium_parser import SeleniumParser
from gxmd.entities.manga import Manga
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.entities.manga_selector import MangaSelector
from gxmd.utils import read_json, extract_domain, get_config_path


class MangaDownloader:
    """
    A class to manage the downloading of manga chapters from supported websites.

    Attributes:
        manga (Manga): manga dataclass object.
        download_manager (DownloadManager): Manages the downloading of files.
        parser: HTML Parser.
    """
    manga: Manga = None

    @staticmethod
    def get_parser(manga_selector: MangaSelector, manga_link: str) -> IMangaParser:
        if manga_selector.render:
            return SeleniumParser(manga_selector, manga_link)
        return RequestParser(manga_selector, manga_link)

    def __init__(self, manga_link: str, manga_selector: MangaSelector, download_manager: DownloadManager):
        """
        Initializes the MangaDownloader object with manga link, selector, and download manager.

        Args:
            manga_link (str): URL to the manga's main page.
            manga_selector (MangaSelector): Selector configuration for the manga.
            download_manager (DownloadManager): The download manager instance for handling downloads.
        """
        self.download_manager = download_manager
        self.parser = MangaDownloader.get_parser(manga_selector, manga_link)
        self._set_manga_info(manga_link)

    def _set_manga_info(self, manga_url: str):
        title = self.parser.parse_manga_name()
        chapters: list[MangaChapter] = self.parser.parse_chapters_info()
        self.manga = Manga(title=title, url=manga_url, chapters=chapters)

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

    def download_chapters(self, start: int = None, end: int = None):
        """
        Downloads the specified range of chapters.

        Args:
            start (int, optional): Starting index of chapters to download. Defaults to 0.
            end (int, optional): Ending index of chapters to download. Defaults to the last chapter.
        """
        start = start - 1 if start else 0
        end = end or len(self.chapters)
        for i in range(start, end):
            self._download_chapter(i)
        self.download_manager.wait_all_downloads()
        time.sleep(0.2)
        print("\nDownload completed ^^")

    def download_chapter(self, index: int):
        """
        method to download a specific chapter by index.

        Args:
            index (int): Index of the chapter in the list.
        """
        self._download_chapter(index - 1)

    def _download_chapter(self, index: int):
        """
        Private method to download a specific chapter by index.

        Args:
            index (int): Index of the chapter in the list.
        """
        chapter = self.chapters[index]
        images_to_download = self.parser.parse_chapter_images(chapter.link)

        start_message = f"Downloading {chapter.name.capitalize()}" \
            if chapter.name.lower().startswith('chapter') else \
            f"Downloading Chapter {chapter.name}"
        self.download_manager.download_files(
            links=images_to_download,
            headers={'Referer': chapter.link, 'User-Agent': USER_AGENT, 'Accept-Encoding': 'identity'},
            path=os.path.join(self.download_manager.downloads_directory, self.manga.title, chapter.name),
            start_message=start_message,
        )

    @classmethod
    def load_manga(cls, manga_link: str, download_manager: DownloadManager, config_file: str | None):
        """
        Class method to load manga configuration and return an instance of MangaDownloader.

        Args:
            manga_link (str): URL to the manga's main page.
            download_manager (DownloadManager): The download manager instance.
            config_file (str): Path to the JSON configuration file.

        Returns:
            MangaDownloader: An instance of MangaDownloader.

        Raises:
            Exception: If the website is not supported.
        """
        if config_file is None:
            config_file = get_config_path('selectors.json')
        manga_selectors = read_json(config_file)
        domain_name = extract_domain(manga_link)
        manga_selector_dict = manga_selectors.get(domain_name)

        if manga_selector_dict is not None:
            manga_selector = MangaSelector(**manga_selector_dict)
            return cls(manga_link, manga_selector, download_manager)
        else:
            raise Exception('Website not supported')
