# Project Tasks

## Phase 1: Environment & STT Setup ✅ COMPLETED
- [x] Set up Python virtual environment and install dependencies (`fastapi`, `langchain`, `boto3`).
- [x] Configure AWS Bedrock client connection.
- [x] Implement a basic endpoint `/upload-audio` that accepts an audio file.
- [x] Integrate Amazon Transcribe for Audio -> Text conversion.

## Phase 2: LangChain & AWS Bedrock Implementation ✅ COMPLETED
- [x] S3 버킷 설정 및 오디오 파일 업로드 로직 구현
- [x] Amazon Transcribe 결과를 파싱하여 화자별 텍스트 추출
- [x] LangChain 프롬프트 템플릿 작성: "회의록 요약" (Agent A)
- [x] LangChain 프롬프트 템플릿 작성: "액션 아이템 추출" (Agent B)
  - JSON 출력 형식: `[{"assignee": "name", "task": "description", "due_date": "YYYY-MM-DD", "confidence": float}]`
- [x] 상대적 날짜 표현 처리 로직 ("내일", "다음 주 금요일" -> 절대 날짜 변환)
- [x] LangChain Chain 구축: 텍스트 입력 -> Bedrock (Nova Pro) -> JSON 파싱
- [x] `/process-transcript` 엔드포인트 구현 (STT 결과를 받아 액션 아이템 추출)

## Phase 3: Notion Integration ✅ COMPLETED
- [x] Notion API 클라이언트 설정 (`services/notion.py`)
- [x] Notion Database 구조 확인 및 매핑 로직 구현
  - Status (Select): "To Do", "In Progress", "Done"
  - Assignee (Text)
  - Due Date (Date)
  - Task Description (Title)
  - Confidence (Number)
- [x] 추출된 JSON 데이터를 Notion Page로 생성하는 함수 구현
- [x] Assignee 이름 매칭 로직 (텍스트 태그로 처리)
- [x] `/push-to-notion` 엔드포인트 구현
- [x] 전체 플로우 통합: `/process-full-workflow` 엔드포인트 구현

## Phase 4: Frontend & Connection ✅ COMPLETED
- [x] React 프로젝트 초기 설정 (Vite + Tailwind CSS)
- [x] 파일 업로드 UI 컴포넌트 구현 (드래그 앤 드롭 지원)
- [x] 환경 변수로 백엔드 URL 관리 (`VITE_API_URL`)
- [x] 처리 상태 표시 UI (Uploading -> Completed)
- [x] 에러 핸들링 및 사용자 피드백 UI
- [x] 추출된 액션 아이템 미리보기 기능

## Phase 5: Testing & Refinement ✅ COMPLETED
- [x] 날짜 변환 로직 개선 (프롬프트 명확화)
- [x] 파일 정리 로직 추가 (업로드 후 로컬 파일 삭제)
- [x] Notion 에러 핸들링 개선
- [x] 로깅 시스템 추가 (전체 플로우 추적)
- [ ] 환경 설정 및 실제 AWS/Notion 연동 테스트
- [ ] 샘플 회의 음성 파일로 전체 플로우 검증
- [ ] 에러 케이스 테스트 (잘못된 파일 형식, API 실패, 네트워크 오류)
- [ ] 프롬프트 튜닝 (액션 아이템 추출 정확도 개선)
- [ ] 성능 최적화 (대용량 오디오 파일 처리)

## Phase 6: Deployment (Optional)
- [ ] Docker 컨테이너화
- [ ] AWS EC2/ECS 배포
- [ ] 프론트엔드 정적 호스팅 (S3 + CloudFront)
- [ ] CI/CD 파이프라인 구축