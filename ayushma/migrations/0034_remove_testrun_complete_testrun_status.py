from django.db import migrations, models


def migrate_testrun_status(apps, schema_editor):
    TestRun = apps.get_model("ayushma", "TestRun")
    for testrun in TestRun.objects.all():
        if testrun.complete:
            testrun.status = "completed"
        else:
            testrun.status = "canceled"
        testrun.save()


def reverse_testrun_status(apps, schema_editor):
    TestRun = apps.get_model("ayushma", "TestRun")
    for testrun in TestRun.objects.all():
        if testrun.status == "completed":
            testrun.complete = True
        else:
            testrun.complete = False
        testrun.save()


class Migration(migrations.Migration):
    dependencies = [
        ("ayushma", "0033_project_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="testrun",
            name="status",
            field=models.CharField(
                choices=[
                    ("running", "running"),
                    ("completed", "completed"),
                    ("canceled", "canceled"),
                    ("failed", "failed"),
                ],
                default="running",
                max_length=20,
            ),
        ),
        migrations.RunPython(
            migrate_testrun_status, reverse_code=reverse_testrun_status
        ),
        migrations.RemoveField(
            model_name="testrun",
            name="complete",
        ),
    ]
