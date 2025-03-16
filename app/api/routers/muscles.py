from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models.muscles import Muscle
from app.api.schemas.muscles import MuscleCreate, MuscleResponse

muscles_router = APIRouter(tags=["Muscles"])

@muscles_router.get("/muscles", response_model=list[MuscleResponse])
def get_muscles():
    """Fetch all muscles with image URLs"""
    with session_scope() as session:
        muscles = session.query(Muscle).all()

        return [
            MuscleResponse(
                id=muscle.id,
                name=muscle.name,
                pic=f"/uploads/muscles/{muscle.pic}" if muscle.pic else None
            ) for muscle in muscles
        ]

@muscles_router.post("/muscles", response_model=MuscleResponse, status_code=201)
def create_muscle(data: MuscleCreate):
    """Create a new muscle"""
    with session_scope() as session:
        # Check if muscle already exists
        existing_muscle = session.query(Muscle).filter_by(name=data.name).first()
        if existing_muscle:
            raise HTTPException(status_code=400, detail="Muscle already exists")

        new_muscle = Muscle(id=uuid4(), name=data.name, pic=data.pic)
        session.add(new_muscle)
        session.commit()
        session.refresh(new_muscle)  # Ensures we return the latest DB state
        return MuscleResponse(id=new_muscle.id, name=new_muscle.name, pic=new_muscle.pic)
