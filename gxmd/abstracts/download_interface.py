from abc import ABC, abstractmethod
from collections.abc import Mapping

from gxmd.progressbar import ProgressBar
from gxmd.services.exporter import ExporterBase


class IDownloadManager(ABC):
    """
    This is an abstract base class for a download manager.

    """

    @abstractmethod
    async def download_file_async(self, link: str, headers: Mapping[str, str | bytes], exporter: ExporterBase,
                                  progress: ProgressBar = None) -> None:
        """
        Downloads a file from the given link.

        Parameters:
        - link (str): The URL of the file to be downloaded.
        - referer (str): The referer URL to include in the headers of the HTTP requests.
        - path (str): The local directory path to save the downloaded file.
        - progress (ProgressBar, optional): The progress bar instance to update after the download.

        Returns:
        - None

        """
        pass

    @abstractmethod
    async def download_files_async(self, links: list[str], headers: Mapping[str, str | bytes] | None,
                                   path: str = None) -> None:
        """
        Downloads multiple files from the given list of links.

        Parameters:
        - links (list[str]): A list of URLs of the files to be downloaded.
        - referer (str): The referer URL to include in the headers of the HTTP requests.
        - path (str): The local directory path to save the downloaded file.

        Returns:
        - None

        """
        pass
