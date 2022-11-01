from enum import Enum


class TitleType(str, Enum):
    """Title type enum. """
    MOVIE = "Movie"
    TV_SHOW = "TV Show"
    OTHER = "Other"


class Platform(str, Enum):
    """Platform choices enum. """
    AMAZON_PRIME = "Amazon Prime"
    NETFLIX = "Netflix"
    HULU = "Hulu"
    HBO = "HBO"
    DISNEY_PLUS = "Disney+"
    APPLE_TV = "Apple TV"
    YOUTUBE = "YouTube"
    OTHER = "Other"
