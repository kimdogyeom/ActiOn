# 화자 분리 (Speaker Diarization) 기능 문서

## 개요
ActiOn 서비스는 Amazon Transcribe의 화자 분리 기능을 활용하여 회의 참석자들의 발화를 구분합니다. 이는 "누가 무엇을 말했는지" 파악하여 정확한 작업 할당을 가능하게 하는 핵심 기능입니다.

## Amazon Transcribe Speaker Diarization

### 기능 설명
화자 분리(Speaker Diarization)는 오디오 파일에서 여러 화자를 자동으로 식별하고 구분하는 기술입니다.

### 주요 특징
- **자동 화자 감지**: 최대 10명까지 자동으로 구분
- **화자 라벨링**: spk_0, spk_1, spk_2 등으로 각 화자 식별
- **타임스탬프**: 각 발화의 시작/종료 시간 제공
- **언어 지원**: 한국어(ko-KR) 포함 다양한 언어 지원

### AWS 공식 문서
- [Speaker Diarization 가이드](https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html)
- [API 레퍼런스](https://docs.aws.amazon.com/transcribe/latest/APIReference/API_Settings.html)

## 구현 세부사항

### 1. Transcription Job 설정
```python
self.client.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': audio_file_path},
    MediaFormat='mp3',
    LanguageCode='ko-KR',
    Settings={
        'ShowSpeakerLabels': True,      # 화자 분리 활성화
        'MaxSpeakerLabels': 10,         # 최대 화자 수
        'ChannelIdentification': False  # 단일 채널 오디오
    }
)
```

### 2. 출력 데이터 구조
Amazon Transcribe는 다음과 같은 JSON 구조로 결과를 반환합니다:

```json
{
  "results": {
    "speaker_labels": {
      "speakers": 3,
      "segments": [
        {
          "speaker_label": "spk_0",
          "start_time": "0.5",
          "end_time": "3.2",
          "items": [...]
        },
        {
          "speaker_label": "spk_1",
          "start_time": "3.5",
          "end_time": "7.8",
          "items": [...]
        }
      ]
    },
    "items": [
      {
        "type": "pronunciation",
        "start_time": "0.5",
        "end_time": "0.8",
        "alternatives": [{"content": "안녕하세요"}]
      }
    ]
  }
}
```

### 3. 파싱 로직
`parse_transcript_with_speakers()` 메서드는:
1. Transcribe 결과 JSON을 다운로드
2. `speaker_labels.segments`에서 화자별 세그먼트 추출
3. 각 세그먼트의 타임스탬프 범위 내 단어들을 결합
4. 화자 라벨, 텍스트, 타임스탬프를 포함한 구조화된 데이터 반환

## ActiOn에서의 활용

### 1. 담당자 식별
```python
# 예시 입력
[
  {"speaker": "spk_0", "text": "철수야, 네가 자료조사 해줘"},
  {"speaker": "spk_1", "text": "네, 알겠습니다"}
]

# LLM 분석 결과
{
  "assignee": "철수",
  "task": "자료조사",
  "due_date": null,
  "confidence": 0.9
}
```

### 2. 회의록 생성
화자별로 구분된 텍스트를 사용하여 더 명확한 회의록 생성:
```
[spk_0]: 오늘 회의 안건은 프로젝트 일정 조율입니다.
[spk_1]: 제가 디자인 파트를 맡겠습니다.
[spk_2]: 저는 개발을 담당하겠습니다.
```

### 3. 액션 아이템 추출
LLM이 화자 정보를 활용하여:
- 누가 작업을 할당받았는지 명확히 파악
- 담당자가 불명확한 경우 "Unassigned"로 표시
- 여러 사람이 언급된 경우 문맥 분석

## 제한사항 및 고려사항

### 제한사항
- **최대 화자 수**: 10명까지만 구분 가능
- **오디오 품질**: 낮은 품질의 오디오는 정확도 저하
- **배경 소음**: 소음이 많으면 화자 구분 어려움
- **화자 중첩**: 동시에 말하는 경우 구분 불가

### 권장사항
- 깨끗한 오디오 녹음 (배경 소음 최소화)
- 한 번에 한 사람씩 발화
- 마이크와 적절한 거리 유지
- 지원 포맷: MP3, M4A, WAV

### 비용 고려
- Amazon Transcribe 요금: 분당 과금
- 화자 분리 기능 사용 시 추가 비용 없음
- [AWS Transcribe 요금 정보](https://aws.amazon.com/transcribe/pricing/)

## 테스트 방법

### 1. 샘플 오디오 준비
```bash
# 2-3명이 대화하는 회의 녹음 파일
sample_meeting.mp3
```

### 2. API 테스트
```bash
curl -X POST http://localhost:8000/upload-audio \
  -F "file=@sample_meeting.mp3"
```

### 3. 결과 확인
- 화자가 올바르게 구분되었는지 확인
- 각 화자의 발화 내용이 정확한지 검증
- 타임스탬프가 올바른지 확인

## 문제 해결

### 화자가 제대로 구분되지 않는 경우
1. 오디오 품질 확인
2. MaxSpeakerLabels 값 조정
3. 오디오 전처리 (노이즈 제거)

### 텍스트가 비어있는 경우
1. 파싱 로직 디버깅
2. Transcribe 결과 JSON 구조 확인
3. 타임스탬프 매칭 로직 검증

## 향후 개선 방향
- [ ] 화자 이름 매핑 기능 (spk_0 -> "김철수")
- [ ] 화자 음성 프로필 저장 및 재사용
- [ ] 실시간 스트리밍 화자 분리
- [ ] 화자 감정 분석 추가
