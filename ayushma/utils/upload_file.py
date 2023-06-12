import os

import boto3
from django.conf import settings
from django.core.files.storage import default_storage


def upload_file(file, s3_key):
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        s3.upload_fileobj(file, settings.S3_BUCKET_NAME, s3_key)
        presigned_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": s3_key},
        )
        return presigned_url.split("?")[0]
    except Exception as e:
        print("Error uploading file: ", e)
        print("Fallbacking file to media folder.")

        # open the file in write binary mode
        print(file.closed)
        file_url = default_storage.save(s3_key, file)
        return file_url
