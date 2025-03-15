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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # ✅ Links to User

    # ✅ Relationships
    split = relationship("Split")
    user = relationship("User", back_populates="workout_sessions")  # ✅ User who created the session
    workouts = relationship("Workout", back_populates="session", cascade="all, delete-orphan")
    muscles = relationship("WorkoutSessionMuscle", back_populates="session", cascade="all, delete-orphan")
