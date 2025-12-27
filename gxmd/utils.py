import json
import os
import posixpath
import random
import re
import string
import sys

from gxmd.config import _RE_COMBINE_WHITESPACE


class GXMDownloaderError(Exception):
    """Raised when errors occur."""
    pass


def generate_random_string(length):
    """Generate a random string of the specified length containing letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def read_json(filename: str) -> dict:
    """Read json file and return a dict"""
    with open(filename, 'r') as f:
        data = f.read()
        return json.loads(data)


def get_config_path(filename: str) -> str:
    # Assuming the config file is in the same directory as the main script
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    return os.path.join(script_dir, filename)


def extract_file_extension_url(url: str) -> str:
    """Extract extension from a URL"""
    _, file_extension = posixpath.splitext(url)
    return file_extension


def extract_domain(url: str) -> str:
    """
    Extracts the domain name from a URL using regular expressions.

    Args:
        url (str): The URL from which to extract the domain name.

    Returns:
        str: The extracted domain name.
    """
    pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return ""


def get_threads():
    """ Returns the number of available threads on a posix/win based system """
    if sys.platform == 'win32':
        return int(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return int(os.popen('grep -c cores /proc/cpuinfo').read())


def combine_whitespaces(my_str: str):
    return _RE_COMBINE_WHITESPACE.sub(" ", my_str).strip()
