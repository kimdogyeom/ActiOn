# Service Specification: ActiOn (Team Project Task Manager)

## 1. Project Overview & Background
### 1.1 Problem Statement (The "Pain Point")
- **Target Audience:** University students participating in group projects (Teamplay).
- **Core Problem:** - "Free Riders" (무임승차자): Team members who do not contribute or disappear.
  - **Ambiguity of Responsibility:** Even after meetings, members often ask, "So, what do I have to do?" or deny responsibility later ("I didn't hear that").
  - **Social Cost:** One person's lack of action leads to lowered grades for everyone and severe emotional stress.
- **Current Solutions' Limitation (e.g., Clova Note, Otter.ai):**
  - They only provide **Text Records** (STT) or Summaries.
  - They lack **Enforcement**. Text records are rarely reviewed, and they do not force users to act.
  - They stop at "Record," failing to bridge the gap to "Action."

### 1.2 Solution & Value Proposition
- **Core Concept:** "Talk to Task"
- **Differentiation:**
  - **Automated Enforcement:** Converts verbal commitments directly into assigned tasks in a project management tool (Notion).
  - **Irrefutable Proof:** Tasks are logged with the assignee's name and due date immediately after the meeting, preventing excuses.
  - **Workflow Automation:** Reducing the friction of manually organizing meeting notes and assigning Jira/Notion tickets.

## 2. System Architecture & Data Flow

### Step 1: Input
- **Source:** Audio files (.mp3, .m4a, .wav) uploaded via Web/App.
- **Context:** Recorded files from team meetings.

### Step 2: STT & Diarization (Speech-to-Text)
- **Engine:** Amazon Transcribe (AWS Managed Service)
- **Key Functions:**
  - **Speech-to-Text:** 음성을 텍스트로 변환 (한국어 지원)
  - **Speaker Diarization (화자 분리):** 최대 10명까지 자동으로 화자 구분
    - 각 화자를 spk_0, spk_1, spk_2 등으로 라벨링
    - 각 발화의 시작/종료 타임스탬프 제공
    - "누가 무엇을 말했는지" 정확히 파악하여 작업 할당의 정확도 향상
  - **설정:**
    - `ShowSpeakerLabels: True` - 화자 분리 활성화
    - `MaxSpeakerLabels: 10` - 최대 10명까지 구분
    - `LanguageCode: ko-KR` - 한국어 인식
  - **참고:** [AWS Transcribe Speaker Diarization 문서](https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html)

### Step 3: The Brain (LangChain + AWS Bedrock)
- **Model:** Claude 3 (via AWS Bedrock).
- **Process:** The system utilizes two distinct Agents (or Chains):
  1.  **Agent A (Summarizer):** Summarizes the overall context of the meeting for record-keeping.
  2.  **Agent B (Action Extractor):**
      - **Input:** Transcribed text with speaker labels.
      - **Goal:** Extract specific "Action Items."
      - **Logic:** Identify sentences containing a Subject (Who), a Task (What), and a Timeframe (When).
      - **Handling Relative Dates:** Convert terms like "tomorrow," "next Friday" into absolute dates (YYYY-MM-DD) based on the upload date.
      - **Handling Ambiguity:** If the assignee is unclear, mark as "Unassigned" for manual review.

### Step 4: Output Integration (Notion API)
- **Target:** A specific Notion Database (Kanban Board format).
- **Action:** Create a new Page for each extracted item.
- **Mapping:**
  - `Title` -> Task Description (e.g., "PPT 초안 작성")
  - `Assignee` -> Mapped Notion User (or Text tag)
  - `Due Date` -> ISO 8601 Date format
  - `Status` -> Default to "To Do"

## 3. Detailed Logic for AI Agents

### 3.1 Action Item Extraction Logic
The AI must distinguish between casual conversation and commitment.
- **Example:**
  - *Audio:* "철수야, 이거 재밌겠다." (Casual -> Ignore)
  - *Audio:* "철수야, 네가 자료조사 해서 금요일까지 공유해줘." (Commitment -> Extract)
  - **Extraction Result:** `{ "assignee": "철수", "task": "자료조사 공유", "due_date": "2025-XX-XX" }`

### 3.2 "Why not ChatGPT?" (Defense Logic)
- Unlike a simple ChatGPT prompt, this system:
  1.  **Integrates Local Context:** Connects directly to the team's specific Notion workspace.
  2.  **Structuring:** Forces unstructured speech into structured JSON data valid for API payloads.
  3.  **Automation:** Removes the human step of "Copying AI response -> Pasting to Notion."