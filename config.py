from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


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
    
    def get_aws_client_kwargs(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        AWS 클라이언트 인증 파라미터 반환
        .env에 엑세스 키가 있으면 사용하고, 없으면 IAM 역할 사용
        
        Args:
            service_name: AWS 서비스 이름 (예: 's3', 'transcribe', 'bedrock-runtime')
        
        Returns:
            boto3 클라이언트 생성에 필요한 kwargs
        """
        client_kwargs = {'region_name': self.aws_region}
        
        if service_name:
            client_kwargs['service_name'] = service_name
        
        if self.aws_access_key_id and self.aws_secret_access_key:
            client_kwargs['aws_access_key_id'] = self.aws_access_key_id
            client_kwargs['aws_secret_access_key'] = self.aws_secret_access_key
        
        return client_kwargs


settings = Settings()
