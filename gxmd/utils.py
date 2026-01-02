import json
import os
import posixpath
import random
import re
import string
import sys
from urllib.parse import urlparse

from selectolax.parser import HTMLParser

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
    """Extract extension from a URL, ignoring query parameters"""
    path = urlparse(url).path
    _, file_extension = posixpath.splitext(path)
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


def is_script_rendered_images(tree: HTMLParser, threshold=0.5) -> bool:
    """
    Detects if a website wraps images in scripts.

    Args:
        tree (HTMLParser): Raw HTML string.
        threshold (float): Ratio of hidden images to visible images to trigger 'True'.
                           If 50% of detected URLs are only in scripts, return True.
    """

    # 1. Get all standard <img> src attributes
    # Using a set for O(1) lookups
    visible_imgs = {
        node.attributes.get('src')
        for node in tree.css('img')
        if node.attributes.get('src')
    }

    # 2. Extract potential image URLs from <script> tags
    # Regex for common image extensions (add more if needed)
    img_pattern = re.compile(r'https?://[^\s"\'<>]+?\.(?:jpg|jpeg|png|webp)')

    script_img_candidates = set()
    for script in tree.css('script'):
        if script.text(strip=True):
            matches = img_pattern.findall(script.text())
            script_img_candidates.update(matches)

    # 3. Analyze the difference
    if not script_img_candidates:
        return False

    # Identify images that are IN SCRIPTS but NOT IN TAGS
    hidden_images = script_img_candidates - visible_imgs

    total_images_found = len(script_img_candidates) + len(visible_imgs)
    if total_images_found == 0:
        return False

    # Calculate "Hidden Ratio"
    # If we found 100 images in scripts and 0 in tags, ratio is 1.0 (100% hidden)
    hidden_ratio = len(hidden_images) / len(script_img_candidates) if script_img_candidates else 0

    is_hidden = len(hidden_images) > 0 and hidden_ratio > threshold

    return is_hidden
