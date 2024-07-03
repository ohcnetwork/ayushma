import os
from io import BytesIO
from typing import Optional

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from PyPDF2 import PdfReader

from ayushma.utils.openaiapi import get_embedding
from ayushma.utils.vectordb import VectorDB


def read_document(url):
    filename = os.path.basename(url.split("?")[0])
    if filename.endswith(".pdf"):  # Handle pdf files
        print("PDF file detected")
        response = requests.get(url)
        print(response)
        pdf_reader = PdfReader(BytesIO(response.content))
        text = ""
        for i in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[i]
            text += page.extract_text()
        document_text = text
    else:  # Handle txt and md files
        if url.startswith("http"):
            response = requests.get(url)
            document_text = response.text
        else:
            with open(os.path.join(settings.MEDIA_ROOT, "documents", url), "r") as f:
                document_text = f.read()

    return document_text


def upsert(
    external_id: str,
    document_id: int,
    s3_url: Optional[str] = None,
    url: Optional[str] = None,
    text: Optional[str] = None,
):
    """
    Upserts the contents of a file, URL, or text to a vector index with the specified external ID.

    Args:
        external_id (str): The external ID to use when upserting to the vector index.
        document_id (int): The external_id of the document that is to be upserted (external_id of the doc is added to the metadata)
        s3_url (str, optional): The S3 URL of the file to upsert. Defaults to None.
        url (str, optional): The URL of the website to upsert. Defaults to None.
        text (str, optional): The text content to upsert. Defaults to None.

    Raises:
        Exception: If none of s3_url, url, or text is provided.

    Returns:
        None
    """

    print("Processing...")

    document_lines = []

    if s3_url:
        document_text = read_document(s3_url)
        document_lines = document_text.strip().splitlines()
    elif url:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        document_lines = soup.get_text().strip().splitlines()

    elif text:
        document_lines = text.strip().splitlines()
    else:
        raise Exception("Either filepath, url or text must be provided")

    if len(document_lines) == 0:
        raise Exception(
            "[Upsert] No text found in the document. Please check the document."
        )
    print(document_lines)

    batch_size = (
        100  # process everything in batches of 100 (creates 100 vectors per upset)
    )

    print("Upserting to vector collection...")

    for i in range(0, len(document_lines), batch_size):
        lines_batch = document_lines[i : i + batch_size]  # get batch of lines and IDs
        lines_batch = [
            line.strip() for line in lines_batch if line.strip()
        ]  # remove blank lines

        embeds = get_embedding(lines_batch)
        partition_name=str(external_id).replace("-", "_")

        VectorDB().insert(
            vectors=embeds,
            texts=lines_batch,
            subject=str(document_id),
            partition_name=partition_name,
        )

    print("Finished upserting to vectorDB")
