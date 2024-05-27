from abc import ABC, abstractmethod
from collections.abc import Mapping

from gxmd.progressbar import ProgressBar


class IDownloadManager(ABC):
    """
    This is an abstract base class for a download manager.

    """

    @staticmethod
    @abstractmethod
    def download_file(link: str, headers: Mapping[str, str | bytes], path: str = None,
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
    def download_files(self, links: [str], headers: Mapping[str, str | bytes] | None, path: str = None) -> None:
        """
        Downloads multiple files from the given list of links.

        Parameters:
        - links ([str]): A list of URLs of the files to be downloaded.
        - referer (str): The referer URL to include in the headers of the HTTP requests.
        - path (str): The local directory path to save the downloaded file.

        Returns:
        - None

        """
        pass
