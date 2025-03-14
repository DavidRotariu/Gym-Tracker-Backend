from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class WorkoutCreate(BaseModel):
    exercise_id: UUID
    reps: Optional[List[int]] = None
    weights: Optional[List[int]] = None

class WorkoutResponse(BaseModel):
    id: UUID
    exercise_id: UUID
    reps: Optional[List[int]]
    weights: Optional[List[int]]
    date: datetime
