from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

class ExerciseCreate(BaseModel):
    name: str
    pic: Optional[str] = None
    tips: Optional[str] = None
    equipment: Optional[str] = None
    favourite: Optional[bool] = False
    muscle_id: UUID
    secondary_muscles: Optional[List[UUID]]

class ExerciseSecondaryMuscleResponse(BaseModel):
    muscle_id: UUID
    name: str

class ExerciseResponse(BaseModel):
    id: UUID
    name: str
    pic: Optional[str]
    tips: Optional[str]
    equipment: Optional[str]
    favourite: bool
    primary_muscle: ExerciseSecondaryMuscleResponse
    secondary_muscles: List[ExerciseSecondaryMuscleResponse]  # ✅ Returns full muscle details
