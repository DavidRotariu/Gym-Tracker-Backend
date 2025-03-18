from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class UserFavoriteExercise(Base):
    __tablename__ = "user_favorite_exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)

    # ✅ Relationships
    user = relationship("User", back_populates="favorite_exercises")
    exercise = relationship("Exercise", back_populates="favorited_by")
