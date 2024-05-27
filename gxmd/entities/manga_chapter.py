from dataclasses import dataclass


@dataclass(frozen=True)
class MangaChapter:
    """Represents a manga chapter"""
    name: str
    link: str
