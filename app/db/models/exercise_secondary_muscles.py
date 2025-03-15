from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class ExerciseSecondaryMuscle(Base):
    __tablename__ = "exercise_secondary_muscles"

    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), primary_key=True)
    muscle_id = Column(UUID(as_uuid=True), ForeignKey("muscles.id"), primary_key=True)

    # ✅ Relationships
    exercise = relationship("Exercise", back_populates="secondary_muscles")
    muscle = relationship("Muscle")
