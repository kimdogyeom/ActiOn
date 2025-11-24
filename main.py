from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
import logging
from pathlib import Path
from datetime import datetime
from services.stt import TranscriptionService
from services.bedrock import BedrockService
from services.s3 import S3Service
from services.llm import LLMService
from services.notion import NotionService
from models import (
    UploadResponse, 
    TranscriptionResponse, 
    ProcessTranscriptRequest,
    ProcessTranscriptResponse,
    PushToNotionRequest,
    PushToNotionResponse,
    SaveDestination,
    TaskResponse,
    TaskUpdateRequest,
    TasksResponse
)
from config import settings
from database import init_db, get_db, Task, TaskStatus

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ActiOn API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 디렉토리 생성
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 서비스 초기화
transcription_service = TranscriptionService()
bedrock_service = BedrockService()
s3_service = S3Service()
llm_service = LLMService()
notion_service = NotionService()

# 데이터베이스 초기화
init_db()


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "service": "ActiOn API"}


@app.post("/upload-audio", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload audio file and start transcription process.
    
    Args:
        file: Audio file (.mp3, .m4a, .wav)
        
    Returns:
        UploadResponse with job information
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # 파일 확장자 검증
    allowed_extensions = ['.mp3', '.m4a', '.wav']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        logger.warning(f"Invalid file format: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # 고유한 파일명 생성
        job_name = f"transcription_{uuid.uuid4().hex[:8]}"
        file_path = UPLOAD_DIR / f"{job_name}{file_ext}"
        
        logger.info(f"Saving file to: {file_path}")
        
        # 로컬에 파일 저장
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # S3에 업로드
        s3_object_name = f"audio/{job_name}{file_ext}"
        logger.info(f"Uploading to S3: {s3_object_name}")
        s3_uri = s3_service.upload_file(str(file_path), s3_object_name)
        
        # Amazon Transcribe 작업 시작
        logger.info(f"Starting transcription job: {job_name}")
        transcription_result = transcription_service.transcribe_audio(s3_uri, job_name)
        
        # 로컬 파일 삭제
        try:
            file_path.unlink()
            logger.info(f"Deleted local file: {file_path}")
        except Exception:
            pass
        
        if transcription_result['status'] == 'success':
            logger.info(f"Transcription completed: {job_name}")
            return UploadResponse(
                message="File uploaded and transcription completed.",
                job_name=job_name,
                status="transcribed"
            )
        else:
            logger.error(f"Transcription failed: {transcription_result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=transcription_result.get('error', 'Transcription failed')
            )
        
    except Exception as e:
        logger.error(f"Error in upload_audio: {str(e)}", exc_info=True)
        # 에러 발생시에도 파일 정리
        if 'file_path' in locals():
            try:
                file_path.unlink()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-transcript", response_model=ProcessTranscriptResponse)
async def process_transcript(request: ProcessTranscriptRequest):
    """
    Process transcription result to extract action items.
    
    Args:
        request: ProcessTranscriptRequest with job_name
        
    Returns:
        ProcessTranscriptResponse with summary and action items
    """
    logger.info(f"Processing transcript for job: {request.job_name}")
    
    try:
        # Transcription 결과 가져오기
        status = transcription_service.client.get_transcription_job(
            TranscriptionJobName=request.job_name
        )
        
        if status['TranscriptionJob']['TranscriptionJobStatus'] != 'COMPLETED':
            logger.warning(f"Transcription not completed: {request.job_name}")
            raise HTTPException(
                status_code=400,
                detail="Transcription not completed yet"
            )
        
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        logger.info(f"Parsing transcript from: {transcript_uri}")
        
        # 화자별 텍스트 파싱
        speaker_texts = transcription_service.parse_transcript_with_speakers(transcript_uri)
        logger.info(f"Parsed {len(speaker_texts)} speaker segments")
        
        # 전체 텍스트 생성 (요약용)
        full_transcript = "\n".join([
            f"{item['speaker']}: {item['text']}"
            for item in speaker_texts
        ])
        
        # 회의록 요약
        logger.info("Generating meeting summary")
        summary = llm_service.summarize_meeting(full_transcript)
        
        # 액션 아이템 추출
        upload_date = request.upload_date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Extracting action items with base date: {upload_date}")
        action_items = llm_service.extract_action_items(speaker_texts, upload_date)
        logger.info(f"Extracted {len(action_items)} action items")
        
        return ProcessTranscriptResponse(
            status="success",
            summary=summary,
            action_items=action_items
        )
        
    except Exception as e:
        logger.error(f"Error in process_transcript: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/push-to-notion", response_model=PushToNotionResponse)
async def push_to_notion(request: PushToNotionRequest):
    """
    Push extracted action items to Notion database.
    
    Args:
        request: PushToNotionRequest with action items
        
    Returns:
        PushToNotionResponse with results
    """
    logger.info(f"Pushing {len(request.action_items)} items to Notion")
    
    try:
        results = notion_service.create_multiple_tasks(request.action_items)
        
        success_count = sum(1 for r in results if r['result']['status'] == 'success')
        logger.info(f"Successfully created {success_count}/{len(results)} tasks in Notion")
        
        return PushToNotionResponse(
            status="success",
            message=f"Successfully created {success_count}/{len(results)} tasks in Notion",
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error in push_to_notion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-full-workflow")
async def process_full_workflow(
    file: UploadFile = File(...),
    destination: str = "notion",
    db: Session = Depends(get_db)
):
    """
    Complete workflow: Upload -> Transcribe -> Extract -> Save (Notion or Internal).
    
    Args:
        file: Audio file
        destination: "notion" or "internal" (default: "notion")
        
    Returns:
        Complete workflow result
    """
    logger.info(f"Starting full workflow for file: {file.filename} with destination: {destination}")
    
    # 1. 파일 업로드 및 STT
    upload_result = await upload_audio(file)
    
    if upload_result.status != "transcribed":
        logger.error("Transcription failed in full workflow")
        raise HTTPException(status_code=500, detail="Transcription failed")
    
    # 2. 액션 아이템 추출
    process_request = ProcessTranscriptRequest(
        job_name=upload_result.job_name,
        upload_date=datetime.now().strftime("%Y-%m-%d")
    )
    process_result = await process_transcript(process_request)
    
    if process_result.status != "success":
        logger.error("Action item extraction failed in full workflow")
        raise HTTPException(status_code=500, detail="Action item extraction failed")
    
    # 3. 선택한 목적지에 저장
    if destination == "notion":
        # Notion에 푸시
        notion_request = PushToNotionRequest(
            action_items=[item.dict() for item in process_result.action_items]
        )
        notion_result = await push_to_notion(notion_request)
        
        logger.info(f"Full workflow completed for job: {upload_result.job_name}")
        
        return {
            "status": "success",
            "job_name": upload_result.job_name,
            "summary": process_result.summary,
            "action_items_count": len(process_result.action_items),
            "destination": "notion",
            "notion_result": notion_result
        }
    else:
        # 내부 DB에 저장
        saved_tasks = []
        for item in process_result.action_items:
            task = Task(
                assignee=item.assignee,
                task=item.task,
                due_date=item.due_date,
                confidence=item.confidence,
                status=TaskStatus.TODO,
                job_name=upload_result.job_name
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            saved_tasks.append({
                "id": task.id,
                "assignee": task.assignee,
                "task": task.task,
                "status": task.status.value
            })
        
        logger.info(f"Saved {len(saved_tasks)} tasks to internal DB")
        
        return {
            "status": "success",
            "job_name": upload_result.job_name,
            "summary": process_result.summary,
            "action_items_count": len(process_result.action_items),
            "destination": "internal",
            "saved_tasks": saved_tasks
        }


@app.get("/health")
def health_check():
    """Check if AWS Bedrock connection is working."""
    try:
        llm = bedrock_service.get_llm()
        return {
            "status": "healthy",
            "bedrock": "connected",
            "model": "amazon.nova-pro-v1:0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/notion/database-info")
def get_notion_database_info():
    """Get Notion database properties for debugging."""
    try:
        properties = notion_service.get_database_properties()
        return {
            "status": "success",
            "properties": properties
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/tasks", response_model=TasksResponse)
def get_tasks(
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all tasks from internal database.
    
    Args:
        status: Filter by status (optional)
        
    Returns:
        List of tasks
    """
    try:
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        task_list = [
            TaskResponse(
                id=task.id,
                assignee=task.assignee,
                task=task.task,
                due_date=task.due_date,
                confidence=task.confidence,
                status=task.status.value,
                job_name=task.job_name,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]
        
        return TasksResponse(
            status="success",
            tasks=task_list,
            total=len(task_list)
        )
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    request: TaskUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update task status.
    
    Args:
        task_id: Task ID
        request: TaskUpdateRequest with new status
        
    Returns:
        Updated task
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.status = TaskStatus(request.status)
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        
        return TaskResponse(
            id=task.id,
            assignee=task.assignee,
            task=task.task,
            due_date=task.due_date,
            confidence=task.confidence,
            status=task.status.value,
            job_name=task.job_name,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Success message
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Task {task_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
