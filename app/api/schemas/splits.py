from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

class SplitCreate(BaseModel):
    name: str
    pic: Optional[str] = None
    muscles: List[dict]  # ✅ List of { muscle_id, nr_of_exercises }

class SplitResponse(BaseModel):
    id: UUID
    name: str
    pic: Optional[str]
    muscles: List[dict]  # ✅ List of { muscle_id, nr_of_exercises }
