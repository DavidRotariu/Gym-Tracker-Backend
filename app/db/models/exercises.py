import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    pic = Column(String, nullable=True)
    tips = Column(String, nullable=True)
    equipment = Column(String, nullable=True)
    favourite = Column(Boolean, default=False)

    muscle_id = Column(UUID(as_uuid=True), ForeignKey("muscles.id"), nullable=False)

    # 🚨 FIX: Use "Muscle" as a string
    muscle = relationship("Muscle", back_populates="exercises")
