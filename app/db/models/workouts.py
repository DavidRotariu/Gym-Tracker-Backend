import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # ✅ Link workouts to a user
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("workout_sessions.id"), nullable=True)  # ✅ Session is optional
    reps = Column(JSON, nullable=False)  # ✅ Stores reps per set as JSON array
    weights = Column(JSON, nullable=False)  # ✅ Stores weights per set as JSON array
    date = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships
    user = relationship("User", back_populates="workouts")  # ✅ Users can have multiple workouts
    exercise = relationship("Exercise", back_populates="workouts")
    session = relationship("WorkoutSession", back_populates="workouts")  # ✅ Workout belongs to a session
