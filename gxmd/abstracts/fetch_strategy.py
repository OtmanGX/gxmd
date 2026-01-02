from abc import ABC, abstractmethod

class FetchStrategy(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Returns the HTML content of the URL."""
        pass

    @abstractmethod
    async def close(self):
        pass
