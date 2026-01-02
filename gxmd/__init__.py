from gxmd.entities.manga import Manga
from gxmd.services.download_manager import DownloadManager
from gxmd.services.exporter import CBZExporter
from gxmd.services.manga_downloader import MangaDownloader


async def parse_manga_info(url: str) -> Manga:
    manga = await MangaDownloader.load_manga_info(url)
    return manga


async def download_all_chapters(job: dict, manga: Manga):
    download_manager = DownloadManager(job.get('id'), with_progress=False)
    manga_downloader = await MangaDownloader.load_manga_from_info(manga, download_manager, CBZExporter)
    await manga_downloader.download_chapters()
