import pinecone
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


def upsert(filepath: str, external_id: str):
    filepath = settings.MEDIA_ROOT + "/" + filepath
    pinecone.init(
        api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT
    )
    print("Initialized Pinecone and OpenAI")

    print(f"Processing...")

    document_lines = read_document(filepath).splitlines()

    batch_size = (
        100  # process everything in batches of 100 (creates 100 vectors per upset)
    )

    print(f"Fetching Pinecone index...")
    if settings.PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(
            settings.PINECONE_INDEX,
            dimension=1536,  # 1536 is the dimension of the text-embedding-ada-002 model
        )
    pinecone_index = pinecone.Index(index_name=settings.PINECONE_INDEX)

    print(f"Upserting to Pinecone index...")

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

    print(f"Finished upserting to Pinecone index")

def deleteNamespace(namespace: str):
    pinecone.init(
        api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT
    )
    pinecone_index = pinecone.Index(index_name=settings.PINECONE_INDEX)
    pinecone_index.delete(delete_all=True, namespace=namespace)