import aiobotocore.session
import asyncio
import io
import logging
import json

from itertools import batched
from PIL import Image
from typing import Union

from refine.decorators import retry
from refine.clients.base import BaseLLMClient
logger = logging.getLogger(__name__)

class BedrockClient(BaseLLMClient):

    # Make the bedrock client a Singleton
    _instance = None
    # Limit to 25 concurrent executions
    _semaphore = asyncio.Semaphore(5)

    def __new__(cls, model_id: str = "amazon.nova-pro-v1:0"):
        if cls._instance is None:
            cls._instance = super(BedrockClient, cls).__new__(cls)
            # TODO: raise this eventually
            cls._instance.token_size = 8192
            cls._instance.model_id = model_id
            cls._instance.session = aiobotocore.session.get_session()
        return cls._instance

    async def chunk(self, text: str) -> list[str]:
        chunks = []
        for batch in batched(text, n=self.token_size):
            chunk = "".join(batch)
            chunks.append(chunk)

        # TODO: this should NOT stay in long term
        #
        # testing against just the first chunk is a mistake,
        # but the current iteration of the tool is unusably slow
        # testing against just the first chunk in the
        # document should reduce the runtime significantly
        chunks = [chunks[0]]
        return chunks

    async def relevant_text(self, contents: str, query: str) -> bool:
        return await self._handle_relevance(contents, query, "text")

    async def relevant_image(self, image: Image, query: str) -> bool:
        return await self._handle_relevance(image, query, "image")

    @retry(max_retries=3, default_return=False)
    async def _handle_relevance(self, content: Union[str, Image], query: str, data_type: str) -> bool:
        """Hidden function to handle relevance checking for different data types."""
        async with self._semaphore:  # Limit concurrent executions
            async with self.session.create_client(
                "bedrock-runtime",
                region_name="us-east-1"
            ) as aws_client:
                try:
                    messages = []
                    prompt = f"""
                    You are a {data_type} classifier. Evaluate if the {data_type} is relevant to the query.
                    Use 'verify' with: 'reason', a string for classification reason, and 'relevant', a boolean indicating relevance.

                    Query: {query}
                    """
                    messages.append({"role": "user", "content": [{"text": prompt}]})

                    if data_type == "text":
                        content_type = {"text": content}
                    elif data_type == "image":
                        buffer = io.BytesIO()
                        content.save(buffer, format="JPEG")
                        buffer = buffer.getvalue()
                        content_type = {"image": {"format": "jpeg", "source": {"bytes": buffer}}}
                    else:
                        raise ValueError("Unsupported data type.")

                    messages.append({"role": "user", "content": [content_type]})
                    tool_config = {"tools": [{"toolSpec": {"name": "verify", "inputSchema": {"json": {"type": "object", "properties": {"reason": {"type": "string"}, "relevant": {"type": "boolean"}}}}}}]}

                    response = await aws_client.converse(modelId=self.model_id, messages=messages, toolConfig=tool_config)
                    tool_call = response["output"]["message"]["content"][-1]["toolUse"]["input"]
                    return tool_call["relevant"]
                except Exception as e:
                    logger.error(f"Error processing {data_type} relevance: {e}")
                    raise
