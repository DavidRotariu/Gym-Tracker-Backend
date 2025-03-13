import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Muscle(Base):
    __tablename__ = "muscles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    pic = Column(String, nullable=True)

    # 🚨 FIX: Use "Exercise" as a string to delay evaluation
    exercises = relationship("Exercise", back_populates="muscle", cascade="all, delete-orphan")
