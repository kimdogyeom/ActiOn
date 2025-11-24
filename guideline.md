# Development Guidelines

## 1. Code Style
- Use Python Type Hints strictly.
- Follow PEP 8 standards.
- Functions should be small and single-responsibility.
- Use Pydantic models for data validation (Input/Output).

## 2. Architecture Principles
- **Modular Design:** Separate the STT logic, LLM processing logic, and Notion integration logic into different modules (e.g., `/services/stt.py`, `/services/llm.py`, `/services/notion.py`).
- **Error Handling:** Even if the STT or LLM fails, the system should not crash. Implement retries for API calls.

## 3. Server Configuration
- **Hardcoding is Prohibited:** Never hardcode server URLs or API Keys.
- Always load configuration from `.env` files.
- When the frontend calls the backend, use `process.env.NEXT_PUBLIC_API_URL` (or equivalent) to reference the server address.

## 4. AI Prompt Engineering (LangChain)
- Use `SystemMessage` to clearly define the persona: "You are an efficient project manager assistant."
- When extracting Action Items, output must be in JSON format strictly to be parsed programmatically.
  - JSON Schema: `[{"assignee": "name", "task": "description", "due_date": "YYYY-MM-DD", "confidence": float}]`
- If the assignee is ambiguous, set `assignee` to "Unassigned".

# 5. 테스트 코드 작성요령
- 테스트 코드는 성공의 결과를 예상하고 작성한 케이스와 실패해야 하는 케이스를 모두 작성하여 검증을 수행한다.

# 6. 문서 작성 요령
- 불필요한 문서작성은 지양한다.
- 사용자에게 보고하기 위한 문서는 최소한으로 작성한다.
- README.md 파일은 사용자가 요청하기 전까지 작성하지 않는다.