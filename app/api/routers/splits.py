from fastapi import APIRouter, HTTPException, Depends, Header
from app.core.supabase import supabase_client
from app.db.database import session_scope
from app.db.models import Muscle, SplitMuscle
from app.db.models.splits import Split
from app.api.schemas.splits import SplitCreate, SplitResponse
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

@splits_router.get("/splits", response_model=list[SplitResponse])
def get_splits(current_user=Depends(get_current_user)):
    """Fetch all splits for an authenticated user"""
    with session_scope() as session:
        splits = session.query(Split).all()
        return [SplitResponse(id=split.id, name=split.name, pic=split.pic) for split in splits]

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
