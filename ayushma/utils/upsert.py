import os
from io import BytesIO
from typing import Optional, List
import pinecone
import requests
from bs4 import BeautifulSoup
from django.conf import settings
import csv
from ayushma.utils.openaiapi import get_embedding
import time
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
def read_columns_from_csv(file_path, column0_header,column1_header,column2_header,column3_header,column4_header,column5_header):
    """
    Reads a specified column from a CSV file into a list.
    :param file_path: Path to the CSV file
    :param column_header: Header of the column to read
    :return: List of values from the specified column
    """
    column0_data = []
    column1_data = []
    column2_data = []
    column3_data = []
    column4_data = []
    column5_data = []
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            column0_data.append(row[column0_header])
            column1_data.append(row[column1_header])
            column2_data.append(row[column2_header])
            column3_data.append(row[column3_header])
            column4_data.append(row[column4_header])
            column5_data.append(row[column5_header])
    return column0_data,column1_data, column2_data,column3_data,column4_data,column5_data
# Example usage:
# csv_file_path = 'your_file_path.csv'
# column_name = 'your_column_name'
# column_values = read_column_from_csv(csv_file_path, column_name)
# print(column_values)
csv_file_path = 'ayushma/utils/test_upsert.csv'  # Replace with your actual CSV file name
column0_name = 'id'
column1_name = 'title'
column2_name = 'author'# Replace with your actual column header name
column3_name = 'context'
column4_name = 'topic'
column5_name = 'url'
id_values,title_values,author_values,context_values,topic_values,url_values= read_columns_from_csv(csv_file_path, column0_name,column1_name, column2_name, column3_name,column4_name,column5_name)
print(len(id_values))
print(len(title_values))
print(len(author_values))
print(len(context_values))
print(len(topic_values))
print(len(url_values))
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
    Upserts the contents of a file, URL, or text to a Pinecone index with the specified external ID.
    Args:
        external_id (str): The external ID to use when upserting to the Pinecone index.
        document_id (int): The external_id of the document that is to be upserted (external_id of the doc is added to the metadata)
        s3_url (str, optional): The S3 URL of the file to upsert. Defaults to None.
        url (str, optional): The URL of the website to upsert. Defaults to None.
        text (str, optional): The text content to upsert. Defaults to None.
    Raises:
        Exception: If none of s3_url, url, or text is provided.
    Returns:
        None
    """
    pinecone.init(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT,
    )
    print("Initialized Pinecone and OpenAI")
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
    print("Fetching Pinecone index...")
    if settings.PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(
            settings.PINECONE_INDEX,
            dimension=1536,  # 1536 is the dimension of the text-embedding-ada-002 model
        )
    pinecone_index = pinecone.Index(index_name=settings.PINECONE_INDEX)
    print("Upserting to Pinecone index...")
    for i in range(0, len(document_lines), batch_size):
        i_end = min(i + batch_size, len(document_lines))  # set end position of batch
        lines_batch = document_lines[i : i + batch_size]  # get batch of lines and IDs
        lines_batch = [
            line.strip() for line in lines_batch if line.strip()
        ]  # remove blank lines
        ids_batch = [f"{document_id}_{n}" for n in range(i, i_end)]  # create IDs
        embeds = get_embedding(lines_batch)  # create embeddings
        meta = [
            {"text": line, "document": str(document_id)} for line in lines_batch
        ]  # prep metadata and upsert batch
        to_upsert = zip(ids_batch, embeds, meta)  # zip together
        pinecone_index.upsert(
            vectors=list(to_upsert), namespace="all_documents"
        )  # upsert to Pinecone
    print("Finished upserting to Pinecone index")
def upsert_base(external_id: str, id_1: List[str], title_1: List[str], author_values_1: List[str], context_values_1: List[str], topic_values_1: List[str], url_values_1: List[str]):
    """
    Upserts contents to a Pinecone index using document IDs, text content, and topics.
    Args:
        external_id (str): The external ID to use when upserting to the Pinecone index.
        column1_data (List[str]): List of document IDs.
        column2_data (List[str]): List of document text contents.
        column3_data (List[str]): List of topics corresponding to each document.
    Returns:
        None
    """
    pinecone.init( api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT )
    print("Initialized Pinecone and OpenAI")
    print("Fetching Pinecone index...")
    if settings.PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(
            settings.PINECONE_INDEX,
            dimension=1536,  # 1536 is the dimension of the text-embedding-ada-002 model
        )
    pinecone_index = pinecone.Index(index_name=settings.PINECONE_INDEX)
    # pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT)
    # if 'default' not in pc.list_indexes().names():
    #     pc.create_index(
    #         name='default',
    #         dimension=1536,
    #         metric='cosine',
    #         spec=PodSpec(
    #             environment=settings.PINECONE_ENVIRONMENT
    #         )
    #     )
    print("Initialized Pinecone")
# Assume column1_data contains document IDs (subjects), column2_data contains document texts (contexts),
# and column3_data contains the corresponding topics for each document.
# ... [previous code for setup] ...
    batch_size = 50
    print("Upserting to Pinecone index...")
    # Ensure that all arrays have the same length before proceeding
    assert len(id_1) == len(title_1) == len(author_values_1) == len(context_values_1) == len(topic_values_1) == len(url_values_1), "Length mismatch among columns."
    for i in range(0, len(context_values_1), batch_size):
        i_end = min(i + batch_size, len(context_values_1))
    # Extract the batch for subjects (IDs), contexts (contents), and topics
        ids_batch = id_1[i:i_end]
        titles_batch = title_1[i:i_end]
        authors_batch = author_values_1
        contexts_batch = context_values_1[i:i_end]
        topics_batch = topic_values_1[i:i_end]
        urls_batch = url_values_1[i:i_end]
    # Create embeddings for the batch of contexts
        embeds = get_embedding(contexts_batch)#embed_documents
    # Prepare metadata for the batch, including subject, context, and topic
        meta = [{"document": title, "author_name":author, "text" : context, "topic": topic,"url":url}
                for title,author,context, topic, url in zip(titles_batch,authors_batch, contexts_batch,topics_batch,urls_batch)]
        # Prepare the data for upserting
        to_upsert = [(id_, embed, meta_) for id_, embed, meta_ in zip(ids_batch, embeds, meta)]
        pinecone_index.upsert(vectors=to_upsert, namespace="all_documents")
        time.sleep(200)
    print("Finished upserting to Pinecone index")
external_id= '28c45a92-9f4a-4d68-bd68-bb7290bcfeef'
#upsert_base(external_id, id_values,title_values,author_values,context_values,topic_values,url_values)
#above is the code to execute the upsert of the test_upsert.csv file to the pinecone database, once upsert done comment it and run application again