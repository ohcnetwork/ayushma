from celery import current_app
from celery.schedules import crontab

from ayushma.tasks.stale_cleanup import clean_stale_test_runs, clean_stale_upsert_doc


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute="*/30"),  # Every 30 minutes
        clean_stale_test_runs.s(),
        name="clean_stale_test_runs",
    )
    sender.add_periodic_task(
        crontab(minute="*/30"),  # Every 30 minutes
        clean_stale_upsert_doc.s(),
        name="clean_stale_upsert_doc",
    )
