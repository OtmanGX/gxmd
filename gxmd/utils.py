import posixpath
import re
from urllib.parse import urlparse

from selectolax.lexbor import LexborHTMLParser
from selectolax.parser import HTMLParser, Node


def minify_html(html: str):
    return "".join(html.split())

def clean_html(tree: HTMLParser):
    """Conservative cleaning - only obvious noise."""
    selectors = [
        "nav", "footer", "aside", "style", "script"
                                           "[class*='advert']", "[class^='ad-']",
        ".sp-wrapper", "[class*='sandpack']"
    ]
    # Clean AFTER finding content to avoid breaking structure
    for sel in selectors:
        for node in tree.css(sel):
            node.decompose()

def find_and_clean_content(tree: HTMLParser, to_parse_images: bool = False):
    soup = find_content(tree, to_parse_images)
    clean_html(tree)

    return soup

def find_content(tree: HTMLParser, to_parse_images: bool = False) -> Node:
    """Generic main content detection - multiple fallbacks."""
    selectors = [
        ".entry-content", "#content", ".content", ".main-content",
        "main", "[role='main']",
    ]

    if to_parse_images:
        selectors.extend([
            '[class*="reader"]', '[class*="viewer"]',  # Common image readers
        ])
    for sel in selectors:
        if node := tree.css_first(sel):
            return node
    best_score = 0
    best_node = tree.body

    for div in tree.css("div"):
        text_len = len(div.text(strip=True))
        if to_parse_images:
            child_count = len(div.css('img'))  # Boost images
        else:
            child_count = len(div.css("li, a"))  # Chapters have many links

        score = text_len + (child_count * 100)

        if score > best_score and text_len > 200:
            best_score = score
            best_node = div
    return best_node

def extract_file_extension_url(url: str) -> str:
    """Extract extension from a URL, ignoring query parameters"""
    path = urlparse(url).path
    _, file_extension = posixpath.splitext(path)
    return file_extension

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


def needs_rendering(html_content: str):
    js_frameworks = [
        r'vue\.js', r'react', r'angular', r'next\.js', r'nuxt\.js',
        r'svelte', r'react-dom', r'@angular', r'preact', r'solid-js'
    ]

    # Check script tags for framework signatures
    framework_match = re.search('|'.join(js_frameworks), html_content, re.IGNORECASE)
    if framework_match:
        return True

    # Check for common data attributes
    data_attrs = [
        r'data-v-[\w-]+',  # Vue
        r'data-reactroot', r'data-react-helmet',  # React
        r'_ngcontent',  # Angular
    ]
    if any(re.search(pattern, html_content, re.IGNORECASE) for pattern in data_attrs):
        return True
    return False


def content_ratio(parser: LexborHTMLParser):
    # Count meaningful content vs boilerplate
    text_content = len(parser.text().strip())
    total_chars = len(parser.html)

    # Very low text ratio suggests JS-generated content
    return text_content / total_chars if total_chars > 0 else 0


def likely_js_rendered(parser: LexborHTMLParser):
    ratio = content_ratio(parser)
    return ratio < 0.05  # Less than 5% meaningful content


def detect_js_rendering(html_content, to_parse_images: bool = True):
    """
    Returns True if site likely needs JS rendering
    """
    checks: list[bool] = []
    parser = LexborHTMLParser(html_content)

    # 1. Framework detection
    checks.append(needs_rendering(html_content))

    # 2. Content ratio
    checks.append(likely_js_rendered(parser))

    # 3. Common placeholders
    placeholders = ['loading...', 'please wait', 'content loading']
    checks.append(any(phrase in html_content.lower() for phrase in placeholders))


    # 4. Manga-specific: check for reader containers without images
    if to_parse_images:
        reader_container = parser.css_first('div.py-8.-mx-5, .reader-container, [class*="chapter"], [class*="reader"]')
        if reader_container and len(reader_container.css('img')) == 0:
            checks.append(True)

    return any(checks)
