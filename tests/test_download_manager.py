import os
import shutil
import unittest
from concurrent.futures import Future, wait, ALL_COMPLETED
from io import StringIO
from unittest.mock import patch

from gxmd.services.download_manager import DownloadManager


class TestDownloadManager(unittest.TestCase):
    def setUp(self):
        self.download_manager = DownloadManager(downloads_directory='downloads', number_of_connections=2,
                                                with_progress=False)

    def tearDown(self):
        # Clean up any downloaded files
        if os.path.isdir('downloads'):
            shutil.rmtree('downloads')

    def test_download_files(self):
        # Mock the download_file method to avoid actual file downloads
        with patch.object(DownloadManager, 'download_file') as mock_download_file:
            links = ['http://example.com/file1.txt', 'http://example.com/file2.txt']
            downloads: [Future] = self.download_manager.download_files(links)
            wait(downloads, return_when=ALL_COMPLETED)
            # Assert that the download_file method was called twice
            self.assertEqual(mock_download_file.call_count, 2)

    def test_wait_all_downloads(self):
        # Mock the ThreadPoolExecutor's shutdown method
        with patch.object(self.download_manager.pool, 'shutdown') as mock_shutdown:
            self.download_manager.wait_all_downloads()
            # Assert that the shutdown method was called with wait=True
            mock_shutdown.assert_called_once_with(wait=True)

    def test_download_file(self):
        # Mock the requests.get method to avoid actual HTTP requests
        with patch('requests.get') as mock_get:
            # Mock the response object
            mock_response = mock_get.return_value
            mock_response.ok = True
            mock_response.raw = StringIO()
            # Call the download_file method
            os.makedirs('downloads')
            self.download_manager.download_file('http://example.com/file.txt', None, 'downloads')
            # Assert that the requests.get method was called with the correct URL
            mock_get.assert_called_once_with('http://example.com/file.txt', headers=None, stream=True)
            # Assert that the file was written to the correct path
            self.assertTrue(os.path.exists('downloads/file.txt'))


if __name__ == '__main__':
    unittest.main()
