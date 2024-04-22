from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from ayushma.models.document import Document
from ayushma.models.enums import StatusChoices
from ayushma.models.testsuite import TestRun


@shared_task(bind=True)
def clean_stale_test_runs(self):
    try:
        # Get testRuns that are created over 6 hours ago and are still in RUNNING state
        test_runs = TestRun.objects.filter(
            created_at__lt=now() - timedelta(hours=6),
            status=StatusChoices.RUNNING,
        )

        # Cancel the testRuns
        for test_run in test_runs:
            print(
                f"Cleaning stale test run: {test_run.id}; Created at: {test_run.created_at}"
            )
            test_run.status = StatusChoices.FAILED
            test_run.save()
    except Exception as e:
        print(f"Error occurred while cleaning stale test runs: {e}")
        raise e


@shared_task(bind=True)
def clean_stale_upsert_doc(self):
    try:
        # Get stale Document objects that are still in UPLOADING state after 6 hours
        documents = Document.objects.filter(
            created_at__lt=now() - timedelta(hours=6),
            uploading=True,
        )

        # Set the documents to failed state
        for document in documents:
            print(
                f"Cleaning stale document: {document.id}; Created at: {document.created_at}"
            )
            document.failed = True
            document.uploading = False
            document.save()

    except Exception as e:
        print(f"Error occurred while cleaning stale test runs: {e}")
        raise e
