# Tech Stack & Environment

## 1. Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (for API server)
- **AI Orchestration:** LangChain (Python)
- **LLM Provider:** AWS Bedrock (via Boto3)
  - Model: Amazon Nova Pro (Implement Amazon Nova Pro using ChatBedrock class in LangChain)
- **STT (Speech-to-Text):** Amazon Transcribe
  - **화자 분리 (Speaker Diarization):** 최대 10명 화자 자동 구분
  - **지원 언어:** 한국어 (ko-KR)
  - **출력 형식:** JSON with speaker labels and timestamps
  - **참고 문서:** https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html

## 2. Frontend (Optional / Simple UI)
- **Framework:** React
- **Styling:** Tailwind CSS

## 3. Integration
- **Notion API:** for creating pages and updating databases.

## 4. Environment Variables (.env)
- `AWS_ACCESS_KEY_ID`: AWS Credentials
- `AWS_SECRET_ACCESS_KEY`: AWS Credentials
- `AWS_REGION`: e.g., us-east-1
- `NOTION_API_KEY`: Notion Integration Token
- `NOTION_DATABASE_ID`: Target Database ID
- `BACKEND_API_URL`: The server address (Managed via env variable as requested)