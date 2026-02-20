"""Database setup and models"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from utils.config import settings

Base = declarative_base()


class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    filename = Column(String, nullable=False)
    doc_type = Column(String)
    doc_type_confidence = Column(Float)
    decision = Column(String)
    score = Column(Float)
    outline_json = Column(JSON)
    evaluation_json = Column(JSON)
    report_json = Column(JSON)
    detection_result_json = Column(JSON)  # MVP1.1


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, nullable=False, index=True)
    question_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    priority = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, nullable=False, index=True)
    finding_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database engine
def get_database_url():
    """Convert DATABASE_URL for async if needed"""
    url = settings.DATABASE_URL
    if settings.DATABASE_TYPE == "sqlite":
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    elif settings.DATABASE_TYPE == "postgres":
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


engine = create_async_engine(get_database_url(), echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
