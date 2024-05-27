import unittest
from unittest.mock import patch, Mock
from gxmd.constants import USER_AGENT
from gxmd.download_manager import DownloadManager
from gxmd.manga_downloader import MangaDownloader
from gxmd.parsers.request_parser import RequestParser
from gxmd.entities.manga import Manga
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.entities.manga_selector import MangaSelector


class TestMangaDownloader(unittest.TestCase):

    def setUp(self):
        self.manga_selector = MangaSelector(
            list_chapters=".chapter-list a",
            chapter_images=".chapter-content img",
            manga_name=".manga-title",
            chapter_link_attr="href",
            chapter_name_attr="href",
            image_link_attr="src",
            render=False
        )
        self.manga_url = "http://example.com/manga"
        self.download_manager = Mock(spec=DownloadManager)
        self.download_manager.downloads_directory = "/path/to/downloads"
        self.parser = Mock(spec=RequestParser)
        self.parser.parse_manga_name.return_value = "Test Manga"
        self.parser.parse_chapters_info.return_value = [
            MangaChapter(name="Chapter 1", link="/chapter1"),
            MangaChapter(name="Chapter 2", link="/chapter2")
        ]

        with patch('gxmd.manga_downloader.MangaDownloader.get_parser', return_value=self.parser):
            self.manga_downloader = MangaDownloader(self.manga_url, self.manga_selector, self.download_manager)

    def test_set_manga_info(self):
        self.manga_downloader._set_manga_info(self.manga_url)
        self.assertEqual(self.manga_downloader.manga.title, "Test Manga")
        self.assertEqual(len(self.manga_downloader.manga.chapters), 2)

    def test_download_chapters(self):
        with patch.object(self.manga_downloader, '_download_chapter') as mock_download_chapter:
            self.manga_downloader.download_chapters()
            self.assertEqual(mock_download_chapter.call_count, 2)
            self.download_manager.wait_all_downloads.assert_called_once()

    def test_download_chapter(self):
        with patch.object(self.manga_downloader, '_download_chapter') as mock_download_chapter:
            self.manga_downloader.download_chapter(1)
            mock_download_chapter.assert_called_once_with(0)

    def test_download_chapter_private(self):
        chapter = MangaChapter(name="Chapter 1", link="/chapter1")
        self.manga_downloader.manga = Manga(title="Test Manga", url=self.manga_url, chapters=[chapter])
        self.parser.parse_chapter_images.return_value = ["image1.jpg", "image2.jpg"]

        with patch('os.path.join', return_value="/path/to/download"):
            self.manga_downloader._download_chapter(0)
            self.download_manager.download_files.assert_called_once_with(
                links=["image1.jpg", "image2.jpg"],
                headers={'Referer': "/chapter1", 'User-Agent': USER_AGENT},
                path="/path/to/download",
                start_message="Downloading Chapter 1"
            )

    @patch('gxmd.manga_downloader.read_json')
    @patch('gxmd.manga_downloader.extract_domain')
    @patch('gxmd.manga_downloader.get_config_path')
    def test_load_manga(self, mock_get_config_path, mock_extract_domain, mock_read_json):
        mock_get_config_path.return_value = "config_path"
        mock_extract_domain.return_value = "example.com"
        mock_read_json.return_value = {
            "example.com": {
                "list_chapters": ".chapter-list a",
                "chapter_images": ".chapter-content img",
                "manga_name": ".manga-title",
                "chapter_link_attr": "href",
                "chapter_name_attr": "href",
                "image_link_attr": "src",
                "render": False
            }
        }
        with patch('gxmd.manga_downloader.MangaDownloader.get_parser', return_value=self.parser):
            manga_downloader = MangaDownloader.load_manga(self.manga_url, self.download_manager, None)
            self.assertIsInstance(manga_downloader, MangaDownloader)
            self.assertEqual(manga_downloader.manga.title, "Test Manga")


if __name__ == '__main__':
    unittest.main()
