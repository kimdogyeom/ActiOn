import boto3
import time
import requests
import logging
from typing import Dict, Optional, List
from config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for handling audio transcription using Amazon Transcribe."""
    
    def __init__(self):
        self.client = boto3.client(**settings.get_aws_client_kwargs('transcribe'))
    
    def transcribe_audio(self, audio_file_path: str, job_name: str) -> Dict:
        """
        Transcribe audio file using Amazon Transcribe with Speaker Diarization.
        
        Speaker Diarization (화자 분리):
        - ShowSpeakerLabels: 화자 분리 기능 활성화
        - MaxSpeakerLabels: 최대 화자 수 (2-10명)
        - 각 발화를 spk_0, spk_1 등으로 라벨링
        
        AWS 공식 문서:
        https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html
        
        Args:
            audio_file_path: S3 URI of the audio file (s3://bucket/key)
            job_name: Unique job name for the transcription
            
        Returns:
            Dict containing transcription status and transcript URI
        """
        try:
            logger.info(f"Starting transcription job: {job_name}")
            
            # Start transcription job with speaker diarization
            response = self.client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': audio_file_path},
                MediaFormat=self._get_media_format(audio_file_path),
                LanguageCode='ko-KR',
                Settings={
                    'ShowSpeakerLabels': True,  # 화자 분리 활성화
                    'MaxSpeakerLabels': 10,     # 최대 10명까지 구분
                    'ChannelIdentification': False  # 단일 채널 오디오
                }
            )
            
            # Wait for completion
            while True:
                status = self.client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                    
                logger.info(f"Transcription job {job_name} status: {job_status}")
                time.sleep(5)
            
            if job_status == 'COMPLETED':
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                logger.info(f"Transcription completed: {job_name}")
                return {
                    'status': 'success',
                    'transcript_uri': transcript_uri,
                    'job_name': job_name
                }
            else:
                logger.error(f"Transcription job failed: {job_name}")
                return {
                    'status': 'failed',
                    'error': 'Transcription job failed'
                }
                
        except Exception as e:
            logger.error(f"Error in transcribe_audio: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_media_format(self, file_path: str) -> str:
        """Extract media format from file path."""
        if file_path.endswith('.mp3'):
            return 'mp3'
        elif file_path.endswith('.m4a'):
            return 'mp4'
        elif file_path.endswith('.wav'):
            return 'wav'
        else:
            return 'mp3'
    
    def parse_transcript_with_speakers(self, transcript_uri: str) -> List[Dict]:
        """
        Parse Amazon Transcribe output to extract speaker-labeled text.
        
        Amazon Transcribe의 화자 분리 결과 구조:
        - results.speaker_labels.segments: 화자별 발화 세그먼트
        - results.items: 개별 단어와 타임스탬프
        
        각 세그먼트는 다음을 포함:
        - speaker_label: "spk_0", "spk_1" 등
        - start_time, end_time: 발화 시작/종료 시간
        - items: 해당 세그먼트의 단어들
        
        Args:
            transcript_uri: URI of the transcript JSON file from Transcribe
            
        Returns:
            List of dicts with speaker label, text, and timestamps
            Example: [
                {
                    'speaker': 'spk_0',
                    'text': '안녕하세요 오늘 회의를 시작하겠습니다',
                    'start_time': 0.5,
                    'end_time': 3.2
                },
                ...
            ]
        """
        try:
            response = requests.get(transcript_uri)
            transcript_data = response.json()
            
            results = transcript_data['results']
            
            # 화자 분리 정보 확인
            if 'speaker_labels' not in results:
                raise Exception("Speaker diarization data not found in transcript")
            
            speaker_labels = results['speaker_labels']
            segments = speaker_labels.get('segments', [])
            speakers = speaker_labels.get('speakers', 0)
            
            print(f"Detected {speakers} speakers in the audio")
            
            # 화자별 텍스트 추출
            speaker_texts = []
            for segment in segments:
                speaker = segment['speaker_label']
                start_time = float(segment['start_time'])
                end_time = float(segment['end_time'])
                
                # 세그먼트 내 아이템들로부터 텍스트 구성
                segment_items = segment.get('items', [])
                
                # 각 아이템의 content를 결합
                words = []
                for item in segment_items:
                    # items 배열에서 해당 인덱스의 단어 찾기
                    item_index = item.get('start_time')
                    for result_item in results['items']:
                        if (result_item.get('type') == 'pronunciation' and 
                            result_item.get('start_time') == item_index):
                            words.append(result_item['alternatives'][0]['content'])
                            break
                
                # 대체 방법: start_time과 end_time 범위로 단어 추출
                if not words:
                    for result_item in results['items']:
                        if result_item.get('type') == 'pronunciation':
                            item_start = float(result_item.get('start_time', 0))
                            item_end = float(result_item.get('end_time', 0))
                            if start_time <= item_start <= end_time:
                                words.append(result_item['alternatives'][0]['content'])
                
                text = ' '.join(words)
                
                if text.strip():
                    speaker_texts.append({
                        'speaker': speaker,
                        'text': text.strip(),
                        'start_time': start_time,
                        'end_time': end_time
                    })
            
            return speaker_texts
            
        except Exception as e:
            raise Exception(f"Failed to parse transcript with speakers: {str(e)}")
