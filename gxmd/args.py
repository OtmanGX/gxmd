import argparse


def create_argparser():
    parser = argparse.ArgumentParser(description="""A manga downloader script that allows users to download 
    manga from supported websites in a convenient and automated manner. 
    This script simplifies the process of downloading manga chapters or entire series 
    by automatically fetching the necessary files from the manga hosting websites""",
                                     prog="gxmd")

    parser.add_argument("url", help="URL of the manga to download")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--chapter', metavar='int', type=int,
                       help='Chapter index to download')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("--start", metavar='int', type=int,
                        help='Starting index of chapters to download')
    group2.add_argument("--end", metavar='int', type=int,
                        help='Ending index of chapters to download')

    parser.add_argument("-d", "--directory", default='Mangas', help="directory path to save the downloaded manga")
    parser.add_argument("-f", "--format", choices=['raw', 'cbz'], default='raw',
                        help="Export format: 'raw' for folders, 'cbz' for compressed archives (default: raw)")

    parser.add_argument("-n", type=int, default=20,
                        help='The number of concurrent downloads allowed')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1.4a')

    # optional bash completion
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass
    return parser
