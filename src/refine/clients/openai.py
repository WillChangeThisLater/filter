import asyncio
import io
import logging
from openai import AsyncOpenAI
from PIL import Image
import base64
from typing import Union
from pydantic import BaseModel

from refine.decorators import retry
from refine.clients.base import BaseLLMClient

logger = logging.getLogger(__name__)

class RelevantTextOutput(BaseModel):
    reason: str
    relevant: bool

class OpenAIClient(BaseLLMClient):
    _instance = None
    _semaphore = asyncio.Semaphore(5)

    def __new__(cls, model: str = "gpt-4.1"):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.model = model
        return cls._instance

    async def chunk(self, text: str) -> list[str]:
        # Assuming similar chunking logic to BedrockClient
        token_size = 8192
        chunks = [text[i:i+token_size] for i in range(0, len(text), token_size)]

        # Temporary solution to process only the first chunk
        return [chunks[0]]

    async def relevant_text(self, content: str, query: str) -> bool:
        return await self._handle_relevance(content, query, "text")

    async def relevant_image(self, image: Image, query: str) -> bool:
        return await self._handle_relevance(image, query, "image")

    @retry(max_retries=3, default_return=False)
    async def _handle_relevance(self, content: Union[str, Image], query: str, data_type: str) -> bool:
        client = AsyncOpenAI()

        async with self._semaphore:
            try:
                if data_type == "text":
                    input_data = [
                        {"role": "system", "content": f"You are a text classifier. Evaluate if the text is relevant to the following query: {query}"},
                        {"role": "user", "content": content}
                    ]
                elif data_type == "image":
                    buffered = io.BytesIO()
                    content.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    input_data = [
                        {"role": "system", "content": f"You are a text classifier. Evaluate if the text is relevant to the following query: {query}"},
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{img_str}"}
                            ]
                        }
                    ]
                else:
                    raise ValueError("Unsupported data type.")

                response = await client.responses.parse(
                    model=self.model,
                    input=input_data,
                    text_format=RelevantTextOutput
                )

                # Assuming the response contains a parsed data structure.
                object: RelevantTextOutput = response.output_parsed
                return object.relevant
            except Exception as e:
                logger.error(f"Error processing {data_type} relevance: {e}")
                raise
