from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class ExerciseCreate(BaseModel):
    name: str
    pic: Optional[str] = None
    tips: Optional[str] = None
    equipment: Optional[str] = None
    favourite: Optional[bool] = False
    muscle_id: UUID

class ExerciseResponse(BaseModel):
    id: UUID
    name: str
    pic: Optional[str]
    tips: Optional[str]
    equipment: Optional[str]
    favourite: bool
    muscle_id: UUID
