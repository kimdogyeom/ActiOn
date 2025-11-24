from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
from datetime import datetime, timedelta
import json
import re
import logging
from services.bedrock import BedrockService

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based text processing using AWS Bedrock."""
    
    def __init__(self):
        self.bedrock_service = BedrockService()
        self.llm = self.bedrock_service.get_llm()
    
    def summarize_meeting(self, transcript: str) -> str:
        """
        Generate meeting summary from transcript.
        
        Args:
            transcript: Full meeting transcript
            
        Returns:
            Summary text
        """
        system_prompt = SystemMessage(content="""당신은 효율적인 프로젝트 관리 어시스턴트입니다.
회의록을 간결하고 명확하게 요약하는 것이 당신의 역할입니다.
주요 논의 사항, 결정 사항, 중요한 포인트를 중심으로 요약하세요.""")
        
        human_prompt = HumanMessage(content=f"""다음 회의 내용을 요약해주세요:

{transcript}

요약 형식:
- 주요 논의 사항
- 결정된 사항
- 기타 중요 포인트""")
        
        response = self.llm.invoke([system_prompt, human_prompt])
        return response.content
    
    def extract_action_items(self, speaker_texts: List[Dict], upload_date: str = None) -> List[Dict]:
        """
        Extract action items from speaker-labeled transcript.
        
        Args:
            speaker_texts: List of dicts with speaker and text
            upload_date: Upload date for relative date conversion (YYYY-MM-DD)
            
        Returns:
            List of action items in JSON format
        """
        if upload_date is None:
            upload_date = datetime.now().strftime("%Y-%m-%d")
        
        base_date = datetime.strptime(upload_date, "%Y-%m-%d")
        
        # 화자별 텍스트를 포맷팅
        formatted_transcript = "\n".join([
            f"[{item['speaker']}]: {item['text']}"
            for item in speaker_texts
        ])
        
        system_prompt = SystemMessage(content=f"""당신은 회의록에서 액션 아이템을 추출하는 전문가입니다.

기준 날짜: {upload_date} ({['월', '화', '수', '목', '금', '토', '일'][base_date.weekday()]}요일)

날짜 변환 규칙:
- "내일" = {(base_date + timedelta(days=1)).strftime("%Y-%m-%d")}
- "모레" = {(base_date + timedelta(days=2)).strftime("%Y-%m-%d")}
- "다음 주" = {(base_date + timedelta(days=7)).strftime("%Y-%m-%d")}
- "이번 주 금요일" = 이번 주 금요일 날짜 계산
- "다음 주 월요일" = 다음 주 월요일 날짜 계산

추출 규칙:
1. 명확한 작업 할당만 추출 (예: "철수야, 네가 자료조사 해줘")
2. 단순 대화는 무시 (예: "이거 재밌겠다")
3. 담당자(Who), 작업(What), 기한(When) 식별
4. 담당자 불명확시 "Unassigned"
5. 기한 없으면 null
6. confidence는 0.0~1.0 (추출 확신도)

JSON 형식으로만 응답:
[
  {{
    "assignee": "담당자 이름",
    "task": "작업 설명",
    "due_date": "YYYY-MM-DD 또는 null",
    "confidence": 0.85
  }}
]""")
        
        human_prompt = HumanMessage(content=f"""다음 회의 내용에서 액션 아이템을 추출하세요:

{formatted_transcript}

JSON 형식으로만 응답하세요.""")
        
        response = self.llm.invoke([system_prompt, human_prompt])
        
        # JSON 파싱
        try:
            # 응답에서 JSON 부분만 추출
            content = response.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                action_items = json.loads(json_match.group())
                logger.info(f"Successfully extracted {len(action_items)} action items")
                return action_items
            else:
                logger.warning("No JSON found in LLM response")
                return []
        except Exception as e:
            logger.error(f"Failed to parse action items: {e}", exc_info=True)
            return []
