from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class SplitMuscle(Base):
    __tablename__ = "split_muscle"

    split_id = Column(UUID(as_uuid=True), ForeignKey("splits.id"), primary_key=True)
    muscle_id = Column(UUID(as_uuid=True), ForeignKey("muscles.id"), primary_key=True)
    nr_of_exercises = Column(Integer, default=0)  # ✅ Tracks the number of exercises in the split

    # ✅ Relationships
    split = relationship("Split", back_populates="muscles")
    muscle = relationship("Muscle", back_populates="splits")
