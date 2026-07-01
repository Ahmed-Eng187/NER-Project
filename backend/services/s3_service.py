import boto3
import uuid
import logging
from botocore.exceptions import ClientError
from backend.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None

    def upload_resume(self, file_content: bytes, filename: str) -> str:
        if not self.s3_client or not self.bucket or settings.AWS_ACCESS_KEY_ID in ["", "your_access_key"]:
            logger.warning("AWS S3 credentials not set (using placeholders). Skipping upload to save locally.")
            return "local-only"

        try:
            object_name = f"resumes/{uuid.uuid4()}_{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_name,
                Body=file_content,
                ServerSideEncryption='AES256'
            )
            logger.info(f"Successfully uploaded {filename} to S3 as {object_name}")
            return object_name
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise Exception("S3 Upload Failed")
