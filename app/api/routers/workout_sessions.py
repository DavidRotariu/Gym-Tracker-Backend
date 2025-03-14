from uuid import uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models.workout_sessions import WorkoutSession
from app.db.models.workout_session_muscle import WorkoutSessionMuscle
from app.db.models.muscles import Muscle
from app.api.schemas.workout_sessions import WorkoutSessionCreate, WorkoutSessionResponse

workout_sessions_router = APIRouter(tags=["Workout Sessions"])

@workout_sessions_router.get("/workout_sessions", response_model=list[WorkoutSessionResponse])
def get_workout_sessions():
    """Fetch all workout sessions"""
    with session_scope() as session:
        sessions = session.query(WorkoutSession).all()
        return [
            WorkoutSessionResponse(
                id=session.id,
                date=session.date,
                split_id=session.split_id,
                muscles=[{"muscle_id": wm.muscle_id, "nr_of_exercises": wm.nr_of_exercises} for wm in session.muscles]
            ) for session in sessions
        ]

@workout_sessions_router.post("/workout_sessions", response_model=WorkoutSessionResponse, status_code=201)
def create_workout_session(data: WorkoutSessionCreate):
    """Create a new workout session"""
    with session_scope() as session:
        new_session = WorkoutSession(
            id=uuid4(),
            split_id=data.split_id
        )
        session.add(new_session)
        session.flush()  # ✅ Ensures new_session.id is available before inserting into WorkoutSessionMuscle

        # ✅ Associate muscles with the workout session
        for muscle_data in data.muscles:
            muscle_id = muscle_data["muscle_id"]
            nr_of_exercises = muscle_data["nr_of_exercises"]

            muscle = session.query(Muscle).filter_by(id=muscle_id).first()
            if not muscle:
                raise HTTPException(status_code=400, detail=f"Muscle with ID {muscle_id} not found")

            session_muscle = WorkoutSessionMuscle(session_id=new_session.id, muscle_id=muscle_id, nr_of_exercises=nr_of_exercises)
            session.add(session_muscle)

        session.commit()
        session.refresh(new_session)
        return WorkoutSessionResponse(
            id=new_session.id,
            date=new_session.date,
            split_id=new_session.split_id,
            muscles=data.muscles
        )
