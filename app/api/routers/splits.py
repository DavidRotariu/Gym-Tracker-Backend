from uuid import uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models.splits import Split
from app.db.models.split_muscle import SplitMuscle
from app.db.models.muscles import Muscle
from app.api.schemas.splits import SplitCreate, SplitResponse

splits_router = APIRouter(tags=["Splits"])

@splits_router.get("/splits", response_model=list[SplitResponse])
def get_splits():
    """Fetch all splits"""
    with session_scope() as session:
        splits = session.query(Split).all()
        return [
            SplitResponse(
                id=split.id,
                name=split.name,
                pic=split.pic,
                muscles=[{"muscle_id": sm.muscle_id, "nr_of_exercises": sm.nr_of_exercises} for sm in split.muscles]
            ) for split in splits
        ]

@splits_router.post("/splits", response_model=SplitResponse, status_code=201)
def create_split(data: SplitCreate):
    """Create a new split"""
    with session_scope() as session:
        # Check if split already exists
        existing_split = session.query(Split).filter_by(name=data.name).first()
        if existing_split:
            raise HTTPException(status_code=400, detail="Split already exists")

        new_split = Split(
            id=uuid4(),
            name=data.name,
            pic=data.pic
        )
        session.add(new_split)
        session.flush()  # ✅ Ensures new_split.id is available before inserting into SplitMuscle

        # ✅ Associate muscles with the split
        for muscle_data in data.muscles:
            muscle_id = muscle_data["muscle_id"]
            nr_of_exercises = muscle_data["nr_of_exercises"]

            muscle = session.query(Muscle).filter_by(id=muscle_id).first()
            if not muscle:
                raise HTTPException(status_code=400, detail=f"Muscle with ID {muscle_id} not found")

            split_muscle = SplitMuscle(split_id=new_split.id, muscle_id=muscle_id, nr_of_exercises=nr_of_exercises)
            session.add(split_muscle)

        session.commit()
        session.refresh(new_split)
        return SplitResponse(
            id=new_split.id,
            name=new_split.name,
            pic=new_split.pic,
            muscles=data.muscles
        )
