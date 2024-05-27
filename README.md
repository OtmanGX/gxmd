# Gx Manga Downloader

This is a universal manga downloader script that allows you to download manga from various websites.
It supports features like specifying the range of chapters to download, downloading to a specific '
directory

## Requirements
- Python 3.6+
## Installation

1. Install as pip package:

    `pip install .`

2. Run program:  

    `gxmd <manga_url>`  
Replace `<manga_url>`  with the URL of the manga.

## Usage
    # help
    gxmd -h
    gxmd --help
    # download to "./downloads/<manga-name-here>" directory
    gxmd -d downloads http://manga-url-here/manga-name
    # download a specific chapter
    gxmd --chapter 5 http://manga-url-here/manga-name
    # download range of chapters
    gxmd --start 5 --end 10 http://manga-url-here/manga-name
    # make 8 simultaneous connections
    gxmd -n 8 http://manga-url-here/manga-name
    # use a specific json file where manga selectors are stored 
    gxmd -c mangas.json http://manga-url-here/manga-name


## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. Make sure to follow the project's coding style and guidelines.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, you can reach out to the project maintainer at [otmangx@yahoo.com](mailto:otmangx@yahoo.com).

Happy manga downloading!