import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from requests import Response
from gxmd.entities.manga_selector import MangaSelector
from gxmd.parsers.request_parser import RequestParser


class TestRequestParser(unittest.TestCase):

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
        self.parser = RequestParser(self.manga_selector, self.manga_url)

    @patch('requests.get')
    def test_load_page(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.content = '<html><head><title>Test Manga</title></head><body></body></html>'
        mock_get.return_value = mock_response

        self.parser._load_page(self.manga_url)
        self.assertIsInstance(self.parser.soup, BeautifulSoup)
        self.assertEqual(self.parser.soup.title.string, "Test Manga")

    @patch('requests.get')
    def test_parse_manga_name(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.content = ('<html><head><title>Test Manga</title></head><body><div class="manga-title">Test '
                                 'Manga Name</div></body></html>')
        mock_get.return_value = mock_response

        self.parser._load_page(self.manga_url)
        manga_name = self.parser.parse_manga_name()
        self.assertEqual(manga_name, "Test Manga Name")

    @patch('requests.get')
    def test_parse_chapters_info(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.content = '''
        <html>
            <head><title>Test Manga</title></head>
            <body>
                <div class="chapter-list">
                    <a href="/chapter2">Chapter 2</a>
                    <a href="/chapter1">Chapter 1</a>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        self.parser._load_page(self.manga_url)
        chapters = self.parser.parse_chapters_info()
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].name, "chapter1")
        self.assertEqual(chapters[0].link, "/chapter1")
        self.assertEqual(chapters[1].name, "chapter2")
        self.assertEqual(chapters[1].link, "/chapter2")

    @patch('requests.get')
    def test_parse_chapter_images(self, mock_get):
        mock_response = Mock(spec=Response)
        mock_response.content = '''
        <html>
            <head><title>Test Manga</title></head>
            <body>
                <div class="chapter-content">
                    <img src="image1.jpg"/>
                    <img src="image2.jpg"/>
                </div>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        images = self.parser.parse_chapter_images(self.manga_url)
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0], "image1.jpg")
        self.assertEqual(images[1], "image2.jpg")


if __name__ == '__main__':
    unittest.main()
