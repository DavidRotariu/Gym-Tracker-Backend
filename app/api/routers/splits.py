from typing import List

from fastapi import APIRouter, HTTPException, Depends, Header
from app.core.supabase import supabase_client
from app.db.database import session_scope
from app.db.models import Muscle, SplitMuscle, User
from app.db.models.splits import Split
from app.api.schemas.splits import SplitCreate, SplitResponse, MuscleResponse, SplitMuscleCreate, SplitMuscleResponse
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

splits_router = APIRouter(tags=["Splits"])

def get_current_user(authorization: str = Header(None)):
    """Verifies and extracts the authenticated user"""
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    user = supabase_client.auth.get_user(token)

    if user.user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user.user  # ✅ Returns authenticated user info

@splits_router.get("/splits", response_model=List[SplitResponse])
def get_splits(current_user=Depends(get_current_user)):
    """Fetch all splits for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        splits = session.query(Split).filter(Split.user_id == db_user.id).all()

        return [
            SplitResponse(
                id=split.id,
                name=split.name,
                pic=split.pic,
                description=" / ".join(
                    [muscle.name for muscle in session.query(Muscle)
                    .join(SplitMuscle, Muscle.id == SplitMuscle.muscle_id)
                    .filter(SplitMuscle.split_id == split.id)
                    .all()]
                ),  # ✅ Returns muscle names as "Chest / Shoulders / Triceps"
                muscles=[
                    SplitMuscleResponse(
                        id=muscle.id,  # ✅ Directly return muscle ID
                        name=muscle.name,
                        pic=f"/uploads/muscles/{muscle.pic}" if muscle.pic else None,
                        nr_of_exercises=sm.nr_of_exercises
                    )
                    for sm in session.query(SplitMuscle).filter(SplitMuscle.split_id == split.id).all()
                    for muscle in session.query(Muscle).filter(Muscle.id == sm.muscle_id).all()
                ]
            ) for split in splits
        ]


@splits_router.post("/splits", response_model=SplitResponse, status_code=201)
def create_split(data: SplitCreate, current_user=Depends(get_current_user)):
    """Create a workout split for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        # ✅ Create the split
        new_split = Split(
            id=uuid4(),
            user_id=db_user.id,
            name=data.name,
            pic=data.pic
        )
        session.add(new_split)
        session.flush()  # ✅ Ensures `new_split.id` is available

        return_muscles = []
        for muscle_data in data.muscles:
            muscle = session.query(Muscle).filter_by(id=muscle_data.muscle_id).first()
            if not muscle:
                raise HTTPException(status_code=400, detail=f"Muscle with ID {muscle_data.muscle_id} not found")

            split_muscle = SplitMuscle(
                split_id=new_split.id,
                muscle_id=muscle.id,
                nr_of_exercises=muscle_data.nr_of_exercises
            )
            session.add(split_muscle)

            return_muscles.append(  # ✅ Now returns expected structure
                SplitMuscleResponse(
                    id=muscle.id,
                    name=muscle.name,
                    pic=muscle.pic,
                    nr_of_exercises=muscle_data.nr_of_exercises
                )
            )

        session.commit()  # ✅ Finalizes changes

        return SplitResponse(
            id=new_split.id,
            name=new_split.name,
            pic=new_split.pic,
            description=" / ".join([m.name for m in return_muscles]),  # ✅ Construct description
            muscles=return_muscles  # ✅ Return full muscle details
        )
