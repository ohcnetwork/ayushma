import json
from abc import ABC, abstractmethod

from django.conf import settings
from pinecone import Pinecone
from pymilvus import MilvusClient


class AbstractVectorDB(ABC):

    client = None
    collection_name = None
    dimensions = 1536
    top_k = 10

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def get_or_create_partition(self, partition_name: str):
        pass

    @abstractmethod
    def insert(self, vectors, texts, subject, partition_name):
        pass

    @abstractmethod
    def get_or_create_collection(self, collection_name: str = None):
        pass

    @abstractmethod
    def sanitize(self, references):
        pass

    @abstractmethod
    def delete_partition(self, partition_name):
        pass

    @abstractmethod
    def delete_subject(self, subject, partition_name):
        pass

    @abstractmethod
    def search(self, embeddings, partition_name, limit=None):
        pass


class MilvusVectorDB(AbstractVectorDB):
    collection_name = settings.MILVUS_COLLECTION

    def initialize(self) -> None:
        self.client = MilvusClient(
            uri=settings.MILVUS_URL,
        )
        self.get_or_create_collection()

    def get_or_create_partition(self, partition_name: str):
        partitions = self.client.list_partitions(collection_name=self.collection_name)
        if partition_name not in partitions:
            self.client.create_partition(
                collection_name=self.collection_name, partition_name=partition_name
            )

    def insert(self, vectors, texts, subject, partition_name):

        self.get_or_create_partition(partition_name)

        data = [
            {"id": i, "vector": vectors[i], "text": texts[i], "subject": subject}
            for i in range(len(vectors))
        ]

        self.client.insert(
            collection_name=self.collection_name,
            data=data,
            partition_name=partition_name,
        )

    def get_or_create_collection(self, collection_name: str = None):
        if collection_name is None:
            collection_name = self.collection_name
        if not self.client.has_collection(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                dimension=self.dimensions,
            )

    def search(self, embeddings, partition_name, limit=None):
        self.get_or_create_partition(partition_name)

        results = self.client.search(
            collection_name=self.collection_name,
            partition_names=[partition_name],
            data=embeddings,
            top_k=limit or self.top_k,
            output_fields=["text", "subject"],
        )
        return results[0]

    def sanitize(self, references):
        sanitized_reference = {}

        for reference in references:
            try:
                document_id = str(reference["entity"]["subject"])
                text = str(reference["entity"]["text"]).replace("\n", " ") + ","
                if document_id in sanitized_reference:
                    sanitized_reference[document_id] += text
                else:
                    sanitized_reference[document_id] = text
            except Exception as e:
                print(f"Error extracting reference: {e}")
                pass

        return json.dumps(sanitized_reference)

    def delete_partition(self, partition_name):
        self.client.drop_partition(
            collection_name=self.collection_name, partition_name=partition_name
        )

    def delete_subject(self, subject, partition_name):
        self.client.delete(
            collection_name=self.collection_name,
            partition_name=partition_name,
            filter='subject in ["' + str(subject) + '"]',
        )


class PineconeVectorDB(AbstractVectorDB):
    collection_name = settings.PINECONE_INDEX

    def initialize(self):
        self.client = Pinecone(
            api_key=settings.PINECONE_API_KEY,
        )
        self.get_or_create_collection()

    def get_or_create_partition(self, partition_name):
        pass

    def insert(self, vectors, texts, subject, partition_name):
        meta = [{"text": texts[i], "document": subject} for i in range(len(vectors))]
        ids = [str(i) for i in range(len(vectors))]
        data = zip(ids, vectors, meta)

        self.client.Index(self.collection_name).upsert(
            vectors=data,
            namespace=partition_name,
        )

    def get_or_create_collection(self, collection_name=None):
        if collection_name is None:
            collection_name = self.collection_name
        indexes = self.client.list_indexes().get("indexes", [])
        print("Indexes", indexes)
        index_names = [index["name"] for index in indexes]
        if collection_name not in index_names:
            self.client.create_index(
                name=collection_name,
                dimension=self.dimensions,
            )

    def search(self, embeddings, partition_name, limit=None):
        index = self.client.Index(self.collection_name)
        result = index.query(
            vector=embeddings,
            namespace=partition_name,
            top_k=limit or self.top_k,
            include_metadata=True,
        )
        return result.matches

    def sanitize(self, references):
        sanitized_reference = {}
        for match in references:
            try:
                document_id = str(match.metadata["document"])
                text = str(match.metadata["text"]).replace("\n", " ") + ","
                if document_id in sanitized_reference:
                    sanitized_reference[document_id] += text
                else:
                    sanitized_reference[document_id] = text
            except Exception as e:
                print(f"Error extracting reference: {e}")
                pass

        return json.dumps(sanitized_reference)

    def delete_partition(self, partition_name):
        index = self.client.Index(self.collection_name)
        index.delete(namespace=partition_name, deleteAll=True)

    def delete_subject(self, subject, partition_name):
        index = self.client.Index(self.collection_name)
        index.delete(
            namespace=partition_name,
            filter={"document": subject},
        )


class VectorDB:
    def __init__(self):
        vector_db_type = settings.VECTOR_DB.lower()
        if vector_db_type == "milvus":
            self.vector_db = MilvusVectorDB()
        elif vector_db_type == "pinecone":
            self.vector_db = PineconeVectorDB()
        else:
            raise ValueError(f"Unsupported VECTOR_DB type: {settings.VECTOR_DB}")
        self.vector_db.initialize()

    def __getattr__(self, name):
        return getattr(self.vector_db, name)
