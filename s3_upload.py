import boto3
import os

def upload_to_s3(filepath, filename):
    AWS_SECRET_KEY = os.environ.get('AWS_KEY')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET')

    session = boto3.Session(
        aws_access_key_id=AWS_SECRET_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    s3 = session.resource('s3')
    s3.meta.client.upload_file(filepath, 'robotaro', filename)
