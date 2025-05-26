import aiofiles
import argparse
import asyncio
import httpx
import logging
import os
import sys
from urllib.parse import urlparse

from atlassian import Confluence, Jira
from filter.clients.base import BaseLLMClient
from filter.clients.openai import OpenAIClient
from filter.clients.bedrock import BedrockClient
from PIL import Image

logger = logging.getLogger(__name__)


async def atlassian_is_relevant(client: BaseLLMClient, uri: str, query: str) -> bool:
    parsed_uri = urlparse(uri)
    atlassian_url = parsed_uri.netloc
    username, password = os.environ["CONFLUENCE_API_USERNAME"], os.environ["CONFLUENCE_API_KEY"]

    if "/browse/" in parsed_uri.path:
        jira_client = Jira(
            url=f'https://{atlassian_url}',
            username=username,
            password=password,
            cloud=True
        )
        # Extract ticket ID and call handle_jira_ticket function
        ticket_id = uri.split('/')[-1]
        ticket = jira_client.issue(ticket_id)
        content = f"{ticket['fields']['summary']} {ticket['fields']['description']}"
        if 'comments' in ticket['fields']:
            content += ' '.join(comment['body'] for comment in jira_client.issue_get_comments(ticket_id)['comments'])
        return await text_is_relevant(client, content, query)

    elif "/wiki/spaces/" in parsed_uri.path:
        confluence_client = Confluence(
            url=f'https://{atlassian_url}',
            username=username,
            password=password,
            cloud=True
        )

        # Extract page or space content
        if "pages" in parsed_uri.path:
            page_id = uri.split('/')[-1]
            page_content = confluence_client.get_page_by_id(page_id, expand='body.storage')['body']['storage']['value']
        else:
            # Handle confluence space content differently
            space_key = parsed_uri.path.split('/')[3]
            pages = confluence_client.get_all_pages_from_space(space_key, start=0, limit=100, expand='body.storage', content_type='page')
            page_content = ' '.join(page['body']['storage']['value'] for page in pages)

        return await text_is_relevant(client, page_content, query)

async def read_uris_from_stdin() -> list[str]:
    uris = []
    for line in sys.stdin:
        uris.append(line.strip())
    return uris

async def read_uris_from_file(file_path: str) -> list[str]:
    async with aiofiles.open(file_path, mode='r') as file:
        contents = await file.readlines()
    return [line.strip() for line in contents]

async def process_directory(client: BaseLLMClient, directory: str, query: str) -> list[str]:
    relevant_uris = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file == 'README.md':
                if await file_is_relevant(client, file_path, query):
                    relevant_uris.append(file_path)
    return relevant_uris

async def file_is_relevant(client: BaseLLMClient, file_name: str, query: str) -> bool:
    extension = file_name.split('.')[-1].lower()
    if extension in ['jpg', 'jpeg', 'png']:
        return await image_is_relevant(client, file_name, query)
    else:
        return await text_file_is_relevant(client, file_name, query)

async def text_is_relevant(client: BaseLLMClient, text: str, query: str) -> bool:
    chunks = await client.chunk(text)
    tasks = [client.relevant_text(chunk, query) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    return any(results)

async def url_is_relevant(client: BaseLLMClient, uri: str, query: str) -> bool:
    async with httpx.AsyncClient() as httpx_client:
        try:
            response = await httpx_client.get(uri, follow_redirects=True)
            response.raise_for_status()  # This will handle HTTP errors if not 200
            relevant = await text_is_relevant(client, response.text, query)
            return relevant
        except httpx.HTTPStatusError as ex:
            logger.error(f"HTTP error occurred: {ex}")
            return False
        except httpx.RequestError as ex:
            logger.error(f"Request error occurred: {ex}")
            return False

async def text_file_is_relevant(client: BaseLLMClient, file_name: str, query: str) -> bool:
    async with aiofiles.open(file_name, mode="r", encoding="utf-8", errors="ignore") as fp:
        contents = await fp.read()
    chunks = await client.chunk(contents)
    tasks = [client.relevant_text(chunk, query) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    return any(results)

async def image_is_relevant(client: BaseLLMClient, file_name: str, query: str) -> bool:
    with Image.open(file_name) as image:
        return await client.relevant_image(image, query)


async def uri_is_relevant(client: BaseLLMClient, uri: str, query: str) -> bool:
    if uri.startswith("http"):
        if "atlassian" in uri:
            return await atlassian_is_relevant(client, uri, query)
        return await url_is_relevant(client, uri, query)
    elif uri.lower().endswith(('.jpg', '.jpeg', '.png')):
        return await image_is_relevant(client, uri, query)
    elif os.path.isdir(uri):
        return await process_directory(client, uri, query)
    else:
        return await text_file_is_relevant(client, uri, query)


async def cli():
    parser = argparse.ArgumentParser(description="CLI tool to determine relevance of URIs.")
    parser.add_argument('query', type=str, help="Relevance query to be used")
    parser.add_argument('--input', type=str, help="Optional file path containing URIs")
    parser.add_argument('--provider', type=str, default="openai", help="LLM client provider")

    args = parser.parse_args()

    if args.input:
        uris = await read_uris_from_file(args.input)
    else:
        uris = await read_uris_from_stdin()

    if args.provider == "openai":
        client = OpenAIClient()
    elif args.provider == "bedrock":
        client = BedrockClient()
    else:
        raise NotImplementedError(f"Error - client {args.client} is not implemented")

    tasks = [uri_is_relevant(client, uri, args.query) for uri in uris]
    results = await asyncio.gather(*tasks)

    # Print relevant URIs
    for uri, is_relevant in zip(uris, results):
        if is_relevant:
            print(uri)

def main():
    asyncio.run(cli())

if __name__ == "__main__":
    main()
