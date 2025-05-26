from abc import ABC, abstractmethod
from typing import Union
from PIL import Image
import asyncio

class BaseLLMClient(ABC):
    _instance = None
    _semaphore: asyncio.Semaphore

    @abstractmethod
    async def chunk(self, text: str) -> list[str]:
        """Divide text into manageable chunks."""
        pass

    @abstractmethod
    async def relevant_text(self, content: str, query: str) -> bool:
        """Determine if the text content is relevant to the query."""
        pass

    @abstractmethod
    async def relevant_image(self, image: Image, query: str) -> bool:
        """Determine if the image content is relevant to the query."""
        pass

    @abstractmethod
    async def _handle_relevance(self, content: Union[str, Image], query: str, data_type: str) -> bool:
        """Handle relevance checking across different data types."""
        pass
