import uuid
from sqlalchemy import Column, DateTime, ForeignKey, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("workout_sessions.id"), nullable=False)
    reps = Column(ARRAY(Integer), nullable=True)  # ✅ Stores reps per set
    weights = Column(ARRAY(Integer), nullable=True)  # ✅ Stores weights per set
    date = Column(DateTime, default=datetime.utcnow)

    # ✅ Relationships
    exercise = relationship("Exercise", back_populates="workouts")
    session = relationship("WorkoutSession", back_populates="workouts")  # ✅ Workout belongs to a session
