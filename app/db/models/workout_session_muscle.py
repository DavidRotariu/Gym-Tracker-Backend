from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class WorkoutSessionMuscle(Base):
    __tablename__ = "workout_session_muscle"

    session_id = Column(UUID(as_uuid=True), ForeignKey("workout_sessions.id"), primary_key=True)
    muscle_id = Column(UUID(as_uuid=True), ForeignKey("muscles.id"), primary_key=True)
    nr_of_exercises = Column(Integer, default=0)  # ✅ Number of exercises for this muscle in the session

    # ✅ Relationships
    session = relationship("WorkoutSession", back_populates="muscles")
    muscle = relationship("Muscle")  # Connects to the Muscle table
