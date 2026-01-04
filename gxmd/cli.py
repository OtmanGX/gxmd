#!/home/otmangx/Dev/manga-downloader/.venv/bin/python
# Copyright (C) 2024 BENAYAD OTMANE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import asyncio
import sys
import traceback

from gxmd.args import create_argparser
from gxmd.exceptions import GXMDownloaderError
from gxmd.log import log_error
from gxmd.parsers.request_parser import RequestParser
from gxmd.parsers.strategies.playwright_strategy import HtmlRenderer
from gxmd.services.download_manager import DownloadManager
from gxmd.services.exporter import CBZExporter, RawExporter
from gxmd.services.manga_downloader import MangaDownloader


async def main():
    parser = create_argparser()
    args = parser.parse_args()
    res = 0
    download_manager = None
    try:
        # Select exporter based on argument
        exporter_class = CBZExporter if args.format == 'cbz' else RawExporter

        download_manager = DownloadManager(args.directory, args.n, True)
        manga_downloader = await MangaDownloader.load_manga(args.url, download_manager, exporter_class)
        if args.chapter:
            await manga_downloader.download_chapter(args.chapter)
        elif args.start or args.end:
            await manga_downloader.download_chapters(args.start, args.end)
        else:
            manga_downloader.list_chapters()
            start = input("Starting index to download (default=1): ").strip()
            if start != "" and not start.isdigit():
                raise Exception('A number is required or leave it empty for default value')
            end = input(f"Ending index to download (default={len(manga_downloader.chapters)}): ").strip()
            if end != "" and not end.isdigit():
                raise Exception('A number is required or leave it empty for default value')
            await manga_downloader.download_chapters(
                int(start) if start != "" else 1,
                int(end) if end != "" else len(manga_downloader.chapters)
            )

    except GXMDownloaderError as e:
        log_error(f"error: {e}")
        res = 1
    except KeyboardInterrupt:
        log_error("aborted")
        res = 1
    except Exception as e:
        log_error(f"internal error: {e}")
        res = 2
        traceback.print_exc(file=sys.stderr)

    await RequestParser.close()
    await HtmlRenderer().close()
    if download_manager:
        await download_manager.close()
    return res


def main_cli():
    """Run main() function."""
    sys.exit(asyncio.run(main()))
