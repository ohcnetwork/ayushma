import urllib.request
from typing import Optional

import pinecone
from bs4 import BeautifulSoup
from django.conf import settings
from PyPDF2 import PdfReader
from tqdm.auto import tqdm

from ayushma.utils.openaiapi import get_embedding


def read_document(filepath):
    if filepath.endswith(".pdf"):  # Handle pdf files
        pdf_reader = PdfReader(filepath)
        text = ""
        for i in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[i]
            text += page.extract_text()
        document_text = text
    else:
        with open(filepath, "r") as f:  # Handle txt and md files
            document_text = f.read()

    return document_text


def upsert(
    external_id: str,
    filepath: Optional[str] = None,
    url: Optional[str] = None,
    text: Optional[str] = None,
):
    """
    Upserts the contents of a file, URL, or text to a Pinecone index with the specified external ID.

    Args:
        external_id (str): The external ID to use when upserting to the Pinecone index.
        filepath (str, optional): The path to the file to upsert. Defaults to None.
        url (str, optional): The URL of the website to upsert. Defaults to None.
        text (str, optional): The text content to upsert. Defaults to None.

    Raises:
        ValueError: If none of filepath, url, or text is provided.

    Returns:
        None
    """
    pinecone.init(
        api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT
    )
    print("Initialized Pinecone and OpenAI")

    print("Processing...")

    document_lines = []

    if filepath:
        filepath = settings.MEDIA_ROOT + "/" + filepath
        document_lines = read_document(filepath).splitlines()
    elif url:
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        document_lines = soup.get_text().strip().splitlines()
    elif text:
        document_lines = text.strip().splitlines()
    else:
        raise ValueError("Either filepath, url or text must be provided")

    batch_size = (
        100  # process everything in batches of 100 (creates 100 vectors per upset)
    )

    print("Fetching Pinecone index...")
    if settings.PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(
            settings.PINECONE_INDEX,
            dimension=1536,  # 1536 is the dimension of the text-embedding-ada-002 model
        )
    pinecone_index = pinecone.Index(index_name=settings.PINECONE_INDEX)

    print("Upserting to Pinecone index...")

    for i in tqdm(range(0, len(document_lines), batch_size)):
        i_end = min(i + batch_size, len(document_lines))  # set end position of batch
        lines_batch = document_lines[i : i + batch_size]  # get batch of lines and IDs
        lines_batch = [
            line.strip() for line in lines_batch if line.strip()
        ]  # remove blank lines
        ids_batch = [str(n) for n in range(i, i_end)]  # create IDs
        embeds = get_embedding(lines_batch)  # create embeddings
        meta = [
            {"text": line} for line in lines_batch
        ]  # prep metadata and upsert batch
        to_upsert = zip(ids_batch, embeds, meta)  # zip together
        pinecone_index.upsert(
            vectors=list(to_upsert), namespace=external_id
        )  # upsert to Pinecone

    print("Finished upserting to Pinecone index")
