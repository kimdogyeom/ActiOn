import boto3
from pathlib import Path
from config import settings


class S3Service:
    """Service for handling S3 file uploads."""
    
    def __init__(self):
        # EC2 IAM 역할을 사용하여 자동으로 인증
        self.client = boto3.client(
            's3',
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Upload file to S3 bucket.
        
        Args:
            file_path: Local file path
            object_name: S3 object name
            
        Returns:
            S3 URI of uploaded file
        """
        try:
            self.client.upload_file(file_path, self.bucket_name, object_name)
            return f"s3://{self.bucket_name}/{object_name}"
        except Exception as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
