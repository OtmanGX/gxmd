from gxmd.utils import GXMDownloaderError


class ParseMangaNameException(GXMDownloaderError):
    def __init__(self, manga_name_selector: str):
        super().__init__(f"Couldn't get manga name using this selector {manga_name_selector}")


class ParseChaptersListException(GXMDownloaderError):
    def __init__(self, selector: str):
        super().__init__(f"Couldn't get chapters list using this selector {selector}")


class ParseChapterNameException(GXMDownloaderError):
    def __init__(self, chapter_name_attr: str):
        super().__init__(f"Couldn't get chapter name using this attribute {chapter_name_attr}")


class ParseChapterLinkException(GXMDownloaderError):
    def __init__(self, chapter_link_attr: str):
        super().__init__(f"Couldn't get chapter link using this attribute {chapter_link_attr}")
