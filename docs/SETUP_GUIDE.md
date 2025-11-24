# ActiOn 설정 가이드

## 사전 요구사항

### 1. AWS 계정 설정
- AWS 계정 생성
- IAM 사용자 생성 및 다음 권한 부여:
  - `AmazonTranscribeFullAccess`
  - `AmazonBedrockFullAccess`
  - `AmazonS3FullAccess`

### 2. S3 버킷 생성
```bash
# AWS CLI로 버킷 생성
aws s3 mb s3://your-action-audio-bucket --region us-east-1
```

### 3. Notion 설정
1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 접속
2. "New integration" 클릭
3. Integration 이름 입력 (예: ActiOn)
4. API Key 복사
5. Notion Database 생성:
   - 새 페이지 생성
   - Database - Table 선택
   - 다음 속성 추가:
     - `Name` (Title) - 작업 설명
     - `Status` (Select) - To Do, In Progress, Done
     - `Assignee` (Text) - 담당자 이름
     - `Due Date` (Date) - 마감일
     - `Confidence` (Number) - AI 확신도
6. Database를 Integration에 연결
7. Database ID 복사 (URL에서 확인)

## 백엔드 설정

### 1. 환경 설정
```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일 편집:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-action-audio-bucket
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BACKEND_API_URL=http://localhost:8000
```

### 3. 서버 실행
```bash
uvicorn main:app --reload
```

서버가 http://localhost:8000 에서 실행됩니다.

### 4. API 테스트
```bash
# Health check
curl http://localhost:8000/health

# Notion database 정보 확인
curl http://localhost:8000/notion/database-info
```

## 프론트엔드 설정

### 1. 의존성 설치
```bash
cd frontend
npm install
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일 편집:
```env
VITE_API_URL=http://localhost:8000
```

### 3. 개발 서버 실행
```bash
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 전체 워크플로우 테스트

### 1. 샘플 오디오 준비
- 2-3명이 대화하는 회의 녹음 파일
- 지원 포맷: MP3, M4A, WAV
- 권장: 깨끗한 음질, 배경 소음 최소화

### 2. 웹 UI에서 테스트
1. http://localhost:3000 접속
2. 오디오 파일 업로드
3. 처리 상태 확인
4. 결과 확인 (요약 + 액션 아이템)
5. Notion Database에서 생성된 작업 확인

### 3. API로 직접 테스트
```bash
# 전체 워크플로우 실행
curl -X POST http://localhost:8000/process-full-workflow \
  -F "file=@sample_meeting.mp3"
```

## 문제 해결

### AWS 권한 오류
```
Error: User is not authorized to perform: transcribe:StartTranscriptionJob
```
→ IAM 사용자에게 필요한 권한 부여

### Notion API 오류
```
Error: Could not find database with ID
```
→ Database ID 확인 및 Integration 연결 확인

### 화자 분리 안됨
```
Error: Speaker diarization data not found
```
→ `ShowSpeakerLabels: True` 설정 확인

## 비용 예상

### AWS Transcribe
- 한국어: $0.024 per minute
- 예시: 30분 회의 = $0.72

### AWS Bedrock (Nova Pro)
- Input: $0.0008 per 1K tokens
- Output: $0.0032 per 1K tokens
- 예시: 5K tokens = ~$0.02

### S3
- 저장: $0.023 per GB/month
- 예시: 100MB 오디오 = ~$0.002

**월 예상 비용 (주 2회 회의 기준):** ~$10-20

## 보안 권장사항
- `.env` 파일을 절대 Git에 커밋하지 마세요
- AWS Access Key는 정기적으로 로테이션
- S3 버킷에 적절한 접근 제어 설정
- Notion API Key는 안전하게 보관
