from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # AWS 엑세스 키는 EC2 IAM 역할 사용 시 불필요 (로컬 개발 시에만 사용)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str
    notion_api_key: str
    notion_database_id: str
    backend_api_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
