from uuid import uuid4
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models.workouts import Workout
from app.db.models.exercises import Exercise
from app.api.schemas.workouts import WorkoutCreate, WorkoutResponse

workouts_router = APIRouter(tags=["Workouts"])

@workouts_router.get("/workouts", response_model=list[WorkoutResponse])
def get_workouts():
    """Fetch all workouts"""
    with session_scope() as session:
        workouts = session.query(Workout).all()
        return [
            WorkoutResponse(
                id=workout.id,
                exercise_id=workout.exercise_id,
                reps=workout.reps,
                weights=workout.weights,
                date=workout.date
            ) for workout in workouts
        ]

@workouts_router.post("/workouts", response_model=WorkoutResponse, status_code=201)
def create_workout(data: WorkoutCreate):
    """Create a new workout entry"""
    with session_scope() as session:
        # Check if exercise exists
        exercise = session.query(Exercise).filter_by(id=data.exercise_id).first()
        if not exercise:
            raise HTTPException(status_code=400, detail="Exercise not found")

        new_workout = Workout(
            id=uuid4(),
            exercise_id=data.exercise_id,
            reps=data.reps,
            weights=data.weights
        )
        session.add(new_workout)
        session.commit()
        session.refresh(new_workout)

        return WorkoutResponse(
            id=new_workout.id,
            exercise_id=new_workout.exercise_id,
            reps=new_workout.reps,
            weights=new_workout.weights,
            date=new_workout.date
        )
