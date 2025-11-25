import boto3
from langchain_aws import ChatBedrock
from config import settings


class BedrockService:
    """Service for AWS Bedrock client connection."""
    
    def __init__(self):
        self.bedrock_runtime = boto3.client(**settings.get_aws_client_kwargs('bedrock-runtime'))
        
        self.llm = ChatBedrock(
            client=self.bedrock_runtime,
            model_id="amazon.nova-pro-v1:0",
            model_kwargs={
                "temperature": 0.3,
                "max_tokens": 2000
            }
        )
    
    def get_llm(self) -> ChatBedrock:
        """Return configured LLM instance."""
        return self.llm
