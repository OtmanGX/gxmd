import concurrent.futures as futures
import os
import posixpath
import shutil  # to save file locally
import time
from collections.abc import Mapping
from concurrent.futures import Future
from typing import List
import requests
from gxmd.abstracts.download_interface import IDownloadManager
from gxmd.progressbar import ProgressBar
from gxmd.utils import extract_file_extension_url


class DownloadManager(IDownloadManager):
    def __init__(self, downloads_directory: str, number_of_connections=2, with_progress=False):
        """
        Initializes the DownloadManager with a specified number of connections and an option to display progress.

        Args:
            downloads_directory (str): The base directory where all downloaded files will be stored.
            number_of_connections (int): The number of concurrent downloads allowed.
            with_progress (bool): Whether to display a progress bar for the downloads.
        """
        self.downloads_directory = downloads_directory
        self.number_of_connections = number_of_connections
        self.pool = futures.ThreadPoolExecutor(max_workers=number_of_connections)
        self.with_progress = with_progress

    def download_files(self, links: [str], headers: Mapping[str, str | bytes] = None, path: str = None,
                       start_message: str = None) -> List[Future]:
        """
        Downloads multiple files from a list of URLs using multiple threads.

        Args:
            links ([str]): A list of URLs to download.
            headers (Mapping[str, str | bytes], optional): The headers of the HTTP requests.
            path (str, optional): The local directory path to save the downloaded files.
            start_message (str, optional): Message to print when download starts.

        Creates the directory if it does not exist and initializes a progress bar if required.
        """
        destination_path = path if path else self.downloads_directory
        os.makedirs(destination_path, exist_ok=True)
        progress = None
        while True:
            if self.pool._work_queue.qsize() < self.number_of_connections:
                break
            time.sleep(0.1)
        if self.with_progress:
            progress = ProgressBar(max_val=len(links), start_message=start_message)

        _downloads: List[Future] = []
        for i, link in enumerate(links):
            filename = "{index}{extension}".format(index=i + 1, extension=extract_file_extension_url(link))
            _downloads.append(self.pool.submit(
                self.download_file,
                link,
                headers,
                destination_path,
                filename,
                progress
            ))
        return _downloads

    def wait_all_downloads(self):
        self.pool.shutdown(wait=True)

    @staticmethod
    def download_file(link: str, headers: Mapping[str, str | bytes] = None, destination_path: str = None,
                      filename: str = None,
                      progress: ProgressBar = None):
        """
        Downloads a single file and saves it to a specified path.

        Args:
            link (str): The URL of the file to download.
            headers (Mapping[str, str | bytes], optional): The headers of the HTTP request.
            destination_path (str, optional): The local directory path to save the downloaded file.
            filename (str, optional): filename to save the downloaded file.
            progress (tqdm, optional): The progress bar instance to update after the download.

        Retrieves the file and writes it to the local filesystem. Updates the progress bar if provided.
        """
        res = requests.get(link.strip(), headers=headers, stream=True)
        if res.ok:
            file_name = filename or posixpath.basename(link)
            with open(posixpath.join(destination_path or '', file_name), 'wb') as f:
                shutil.copyfileobj(res.raw, f)
        else:
            print('Error on downloading file', res.status_code, res.reason)
        if progress is not None:
            # Update the progress bar
            progress.update()

    def __del__(self):
        self.pool.shutdown(wait=False, cancel_futures=True)
