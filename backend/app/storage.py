"""S3/Object storage client"""

import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class S3Client:
    """S3-compatible object storage client"""
    
    def __init__(self):
        self.bucket_name = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_secure
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure bucket exists, create if not"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket exists: {self.bucket_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info(f"Creating bucket: {self.bucket_name}")
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                except ClientError as ce:
                    logger.error(f"Error creating bucket: {str(ce)}")
            else:
                logger.error(f"Error checking bucket: {str(e)}")
    
    def generate_presigned_url(self, method: str, params: dict, expires_in: int = 3600) -> str:
        """Generate presigned URL for S3 operation"""
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=method,
                Params=params,
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """Upload file to S3"""
        try:
            self.client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"File uploaded: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return False
    
    def download_file(self, s3_key: str, file_path: str) -> bool:
        """Download file from S3"""
        try:
            self.client.download_file(self.bucket_name, s3_key, file_path)
            logger.info(f"File downloaded: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return False
    
    def delete_object(self, s3_key: str) -> bool:
        """Delete object from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Object deleted: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting object: {str(e)}")
            return False
    
    def list_objects(self, prefix: str = "") -> list:
        """List objects in S3"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []
        except Exception as e:
            logger.error(f"Error listing objects: {str(e)}")
            return []
    
    def get_object_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Get presigned GET URL for object"""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Error generating GET URL: {str(e)}")
            raise


# Global S3 client instance
s3_client = S3Client()
