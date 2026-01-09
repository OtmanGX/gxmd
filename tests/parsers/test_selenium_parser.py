import unittest
from unittest.mock import patch, MagicMock

from gxmd.parsers.selenium_parser import SeleniumParser
from selenium.webdriver.remote.webelement import WebElement

from gxmd.entities.manga_chapter import MangaChapter
from gxmd.entities.manga_selector import MangaSelector


class TestSeleniumParser(unittest.TestCase):

    def setUp(self):
        self.manga_selector = MangaSelector(
            list_chapters=".chapter-list a",
            chapter_images=".chapter-content img",
            manga_name=".manga-title",
            chapter_link_attr="href",
            image_link_attr="src",
            render=False
        )
        self.manga_url = "http://example.com/manga"
        self.timeout = 10

    @patch('selenium.webdriver.Firefox')
    def test_init(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)

        mock_firefox.assert_called_once()
        self.assertEqual(parser.manga_selector, self.manga_selector)
        self.assertEqual(parser.driver, mock_driver)
        self.assertEqual(parser.wait._timeout, self.timeout)

    @patch('selenium.webdriver.Firefox')
    def test_parse_manga_name(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        mock_driver.find_element.return_value.text = "Test Manga"

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        manga_name = parser.parse_manga_name()

        self.assertEqual(manga_name, "Test Manga")

    @patch('selenium.webdriver.Firefox')
    def test_parse_chapters_info(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_element1 = MagicMock(spec=WebElement)
        mock_element1.get_attribute.side_effect = lambda attr: "/chapter1" if attr == "href" else "Chapter 1"
        mock_element2 = MagicMock(spec=WebElement)
        mock_element2.get_attribute.side_effect = lambda attr: "/chapter2" if attr == "href" else "Chapter 2"

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        chapters = parser.parse_chapters_info()

        expected_chapters = [
            MangaChapter(name="Chapter 2", link="/chapter2"),
            MangaChapter(name="Chapter 1", link="/chapter1"),
        ]

        self.assertEqual(chapters, expected_chapters)

    @patch('selenium.webdriver.Firefox')
    def test_parse_chapter_images(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_element1 = MagicMock(spec=WebElement)
        mock_element1.get_attribute.return_value = "image1.jpg"
        mock_element2 = MagicMock(spec=WebElement)
        mock_element2.get_attribute.return_value = "image2.jpg"

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        images = parser.parse_chapter_images("/chapter1")

        expected_images = ["image1.jpg", "image2.jpg"]

        self.assertEqual(images, expected_images)

    @patch('selenium.webdriver.Firefox')
    def test_load_page(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        parser.load_page("http://example.com/chapter1")

        mock_driver.get.assert_called_with("http://example.com/chapter1")

    @patch('selenium.webdriver.Firefox')
    def test_get_elements_attribute(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_element1 = MagicMock(spec=WebElement)
        mock_element1.get_attribute.return_value = "image1.jpg"
        mock_element2 = MagicMock(spec=WebElement)
        mock_element2.get_attribute.return_value = "image2.jpg"

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        attributes = parser._get_elements_attribute(".chapter-content img", "src")

        expected_attributes = ["image1.jpg", "image2.jpg"]

        self.assertEqual(attributes, expected_attributes)

    @patch('selenium.webdriver.Firefox')
    def test_get_elements(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_element1 = MagicMock(spec=WebElement)
        mock_element2 = MagicMock(spec=WebElement)

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        elements = parser._get_elements(".chapter-list a")

        self.assertEqual(elements, [mock_element1, mock_element2])

    @patch('selenium.webdriver.Firefox')
    def test_get_element_content(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_element = MagicMock(spec=WebElement)
        mock_element.text = "Test Content"

        mock_driver.find_element.return_value = mock_element

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        content = parser._get_element_content(".manga-title")

        self.assertEqual(content, "Test Content")

    @patch('selenium.webdriver.Firefox')
    def test_export_html(self, mock_firefox):
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        mock_driver.page_source = "<html></html>"

        parser = SeleniumParser(self.manga_selector, self.manga_url, self.timeout)
        html = parser.export_html()

        self.assertEqual(html, "<html></html>")


if __name__ == '__main__':
    unittest.main()
