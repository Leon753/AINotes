# app/services/s3_service.py
import boto3, os
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_fileobj_to_s3(file_obj, file_key: str) -> str:
    """Uploads a file-like object to S3 and returns its public URL."""
    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET_NAME, file_key)
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"
        return file_url
    except ClientError as e:
        raise Exception(f"Error uploading to S3: {e}")

def delete_file_from_s3(file_key: str) -> None:
    """Deletes the file from S3 given its key."""
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)
    except ClientError as e:
        raise Exception(f"Error deleting file from S3: {e}")