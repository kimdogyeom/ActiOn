from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

# SQLite 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./action.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    """Task status enum."""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class Task(Base):
    """Task model for internal kanban board."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    assignee = Column(String, nullable=False)
    task = Column(String, nullable=False)
    due_date = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    job_name = Column(String, nullable=True)  # 원본 회의 식별용
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
