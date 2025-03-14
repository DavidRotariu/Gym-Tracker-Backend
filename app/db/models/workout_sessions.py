import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    split_id = Column(UUID(as_uuid=True), ForeignKey("splits.id"), nullable=False)

    # ✅ Relationships
    split = relationship("Split")  # A session belongs to one Split
    workouts = relationship("Workout", back_populates="session", cascade="all, delete-orphan")  # Workouts in this session
    muscles = relationship("WorkoutSessionMuscle", back_populates="session", cascade="all, delete-orphan")  # Muscles worked
