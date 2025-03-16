from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class WorkoutCreate(BaseModel):
    exercise_id: UUID  # ✅ Logs which exercise was performed
    reps: List[int]  # ✅ List of reps for each set
    weights: List[float]  # ✅ List of weights corresponding to reps

class WorkoutResponse(BaseModel):
    id: UUID
    exercise_id: UUID
    reps: Optional[List[int]]
    weights: Optional[List[int]]
    date: datetime
