import asyncio
import posixpath
from collections.abc import Mapping

import aiohttp

from gxmd.abstracts.download_interface import IDownloadManager
from gxmd.progressbar import ProgressBar
from gxmd.services.exporter import ExporterBase
from gxmd.utils import extract_file_extension_url


class DownloadManager(IDownloadManager):
    def __init__(self, downloads_directory: str, number_of_connections=20, with_progress=False):
        """
        Initializes the DownloadManager with a specified number of connections and an option to display progress.

        Args:
            downloads_directory (str): The base directory where all downloaded files will be stored.
            number_of_connections (int): The number of concurrent downloads allowed.
            with_progress (bool): Whether to display a progress bar for the downloads.
        """
        self.downloads_directory = downloads_directory
        self.with_progress = with_progress
        self.semaphore = asyncio.Semaphore(number_of_connections)  # Rate limiting (prevents bans)

        self.connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,  # Cache DNS 5min (default 10s often too short)
            enable_cleanup_closed=True  # Default, cleans stale connections
        )
        self.timeout = aiohttp.ClientTimeout(total=10, connect=5)
        self.session = aiohttp.ClientSession(connector=self.connector, timeout=self.timeout)

    async def download_files_async(self, exporter: ExporterBase,
                                   links: list[str], headers: Mapping[str, str | bytes] = None, path: str = None,
                                   start_message: str = None):
        """
        Downloads multiple files from a list of URLs using multiple threads.

        Args:
            exporter (ExporterBase): exporter instance..
            links ([str]): A list of URLs to download.
            headers (Mapping[str, str | bytes], optional): The headers of the HTTP requests.
            path (str, optional): The local directory path to save the downloaded files.
            start_message (str, optional): Message to print when download starts.

        Creates the directory if it does not exist and initializes a progress bar if required.
        """
        progress = None
        if self.with_progress:
            progress = ProgressBar(max_val=len(links), start_message=start_message)

        tasks = [self.download_file_async(url, headers, exporter,
                                          path,
                                          "{index}{extension}".format(index=i + 1,
                                                                      extension=extract_file_extension_url(url)),
                                          progress)
                 for i, url in enumerate(links)]

        img_results = await asyncio.gather(*tasks, return_exceptions=True)
        for filename, exception in img_results:
            if isinstance(exception, Exception):
                print(f"Failed downloading image {filename}: {exception}")

    async def download_file_async(self, link: str,
                                  headers: Mapping[str, str | bytes],
                                  exporter: ExporterBase,
                                  path: str = None,
                                  filename: str = None,
                                  progress: ProgressBar = None):
        """
        Downloads a single file and saves it to a specified path.

        Args:
            link (str): The URL of the file to download.
            headers (Mapping[str, str | bytes], optional): The headers of the HTTP request.
            exporter (ExporterBase): exporter.
            path (str, optional): path where to save the downloaded file.
            filename (str, optional): filename to save the downloaded file.
            progress (tqdm, optional): The progress bar instance to update after the download.

        Retrieves the file and writes it to the local filesystem. Updates the progress bar if provided.
        """
        async with self.semaphore:
            try:
                async with self.session.get(link.strip(), headers=headers) as resp:
                    resp.raise_for_status()
                    img_data = await resp.read()
                    filename = filename or posixpath.basename(link)
                    if progress is not None:
                        # Update the progress bar
                        progress.update()

                    exporter.add_image(img_data, path, filename)
                    return None, None
            except Exception as e:
                return filename, e

    async def close(self):
        await self.session.close()
