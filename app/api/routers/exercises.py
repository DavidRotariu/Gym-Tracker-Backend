from typing import List
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models import Muscle
from app.db.models.exercises import Exercise
from app.api.schemas.exercises import ExerciseCreate, ExerciseResponse, ExerciseSecondaryMuscleResponse

exercises_router = APIRouter(tags=["Exercises"])

@exercises_router.get("/exercises", response_model=List[ExerciseResponse])
def get_exercises():
    """Fetch all exercises with primary and secondary muscles"""
    with session_scope() as session:
        exercises = session.query(Exercise).all()

        return [
            ExerciseResponse(
                id=exercise.id,
                name=exercise.name,
                pic=exercise.pic,
                tips=exercise.tips,
                equipment=exercise.equipment,
                favourite=exercise.favourite,
                primary_muscle=ExerciseSecondaryMuscleResponse(
                    muscle_id=exercise.muscle_id,
                    name=session.query(Muscle.name).filter(Muscle.id == exercise.muscle_id).scalar()
                ),
                secondary_muscles=[
                    ExerciseSecondaryMuscleResponse(
                        muscle_id=sm.muscle_id,
                        name=session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                    )
                    for sm in exercise.secondary_muscles
                ]
            ) for exercise in exercises
        ]


@exercises_router.post("/exercises", response_model=ExerciseResponse, status_code=201)
def create_exercise(data: ExerciseCreate):
    """Create a new exercise"""
    with session_scope() as session:
        # Check if exercise already exists
        existing_exercise = session.query(Exercise).filter_by(name=data.name).first()
        if existing_exercise:
            raise HTTPException(status_code=400, detail="Exercise already exists")

        new_exercise = Exercise(
            id=uuid4(),
            name=data.name,
            pic=data.pic,
            tips=data.tips,
            equipment=data.equipment,
            favourite=data.favourite,
            muscle_id=data.muscle_id
        )
        session.add(new_exercise)
        session.commit()
        session.refresh(new_exercise)  # ✅ Ensures latest DB state
        return ExerciseResponse(
            id=new_exercise.id,
            name=new_exercise.name,
            pic=new_exercise.pic,
            tips=new_exercise.tips,
            equipment=new_exercise.equipment,
            favourite=new_exercise.favourite,
            muscle_id=new_exercise.muscle_id
        )
