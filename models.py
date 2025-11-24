from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal


class TranscriptionResponse(BaseModel):
    """Response model for transcription results."""
    status: str
    transcript_text: Optional[str] = None
    job_name: Optional[str] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for file upload."""
    message: str
    job_name: str
    status: str


class ActionItem(BaseModel):
    """Model for extracted action item."""
    assignee: str
    task: str
    due_date: Optional[str] = None
    confidence: float


class ProcessTranscriptRequest(BaseModel):
    """Request model for processing transcript."""
    job_name: str
    upload_date: Optional[str] = None


class ProcessTranscriptResponse(BaseModel):
    """Response model for transcript processing."""
    status: str
    summary: Optional[str] = None
    action_items: List[ActionItem]
    error: Optional[str] = None


class PushToNotionRequest(BaseModel):
    """Request model for pushing to Notion."""
    action_items: List[Dict[str, Any]]


class PushToNotionResponse(BaseModel):
    """Response model for Notion push operation."""
    status: str
    message: str
    results: List[Dict[str, Any]]


class SaveDestination(BaseModel):
    """Model for save destination choice."""
    destination: Literal["notion", "internal"]  # "notion" or "internal"


class TaskResponse(BaseModel):
    """Response model for internal task."""
    id: int
    assignee: str
    task: str
    due_date: Optional[str] = None
    confidence: Optional[float] = None
    status: str
    job_name: Optional[str] = None
    created_at: str
    updated_at: str


class TaskUpdateRequest(BaseModel):
    """Request model for updating task status."""
    status: Literal["To Do", "In Progress", "Done"]


class TasksResponse(BaseModel):
    """Response model for task list."""
    status: str
    tasks: List[TaskResponse]
    total: int
