from time import sleep

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings

from ayushma.models.document import Document
from ayushma.models.enums import DocumentType
from ayushma.utils.upsert import upsert


@shared_task(bind=True, soft_time_limit=21600)  # 6 hours in seconds
def upsert_doc(self, document_id: str, document_url: str = None):
    try:
        sleep(5)
        if not settings.OPENAI_API_KEY:
            print("OpenAI API key not found. Skipping test run.")
            return

        document: Document = Document.objects.get(external_id=document_id)
        if document.document_type == DocumentType.FILE:
            upsert(
                external_id=document.project.external_id,
                s3_url=document_url,
                document_id=document.external_id,
            )
        elif document.document_type == DocumentType.URL:
            upsert(
                external_id=document.project.external_id,
                url=document.text_content,
                document_id=document.external_id,
            )
        elif document.document_type == DocumentType.TEXT:
            upsert(
                external_id=document.project.external_id,
                text=document.text_content,
                document_id=document.external_id,
            )
        else:
            raise Exception("Invalid document type.")

        document.uploading = False
        document.save()

    except SoftTimeLimitExceeded:
        print("SoftTimeLimitExceeded")
        document.uploading = False
        document.save()
        document.delete()
        return
