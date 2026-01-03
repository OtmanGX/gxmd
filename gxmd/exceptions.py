class GXMDownloaderError(Exception):
    """Raised when errors occur."""
    pass


class GXMTimeoutError(GXMDownloaderError):
    """Raised when a network or rendering request times out."""
    pass

class GXMNetworkError(GXMDownloaderError):
    """Raised when a network request fails (404, 500, etc.)."""
    pass

