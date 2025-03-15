import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Split(Base):
    __tablename__ = "splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, unique=True, nullable=False)
    pic = Column(String, nullable=True)

    muscles = relationship("SplitMuscle", back_populates="split", cascade="all, delete-orphan")
    user = relationship("User", back_populates="splits")
