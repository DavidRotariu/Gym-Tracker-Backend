from datetime import datetime, date, timezone
from typing import List
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import UUID, String, cast, func
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.routers.splits import get_current_user
from app.db.database import session_scope
from app.db.models.users import User
from app.db.models.workouts import Workout
from app.db.models.exercises import Exercise
from app.api.schemas.workouts import WorkoutCreate, WorkoutResponse

workouts_router = APIRouter(tags=["Workouts"])

@workouts_router.get("/workouts/today", response_model=List[WorkoutResponse])
def get_todays_workouts(current_user=Depends(get_current_user)):
    """Retrieve all workouts logged today for the authenticated user"""
    """Fetch all workouts for a specific exercise by the authenticated user"""
    with session_scope() as session:
        # Get user ID as a string
        db_user = session.query(User.id).filter_by(auth_id=current_user.id).scalar()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Get current UTC date range
        now_utc = datetime.now(timezone.utc)
        today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        all_workouts = session.query(Workout).all()

        filtered_workouts = []
        for workout in all_workouts:
            workout_datetime = workout.date.replace(tzinfo=timezone.utc)
            if(workout_datetime >= today_start):
                filtered_workouts.append(workout)

        # workout_responses = []
        # for workout in filtered_workouts:
            # exercise = session.query(Exercise).filter(Exercise.id == workout.exercise_id).first()
            # print(exercise.muscle.name)

        return [
            WorkoutResponse(
                id=workout.id,
                exercise_id=workout.exercise_id,
                reps=workout.reps,
                weights=workout.weights,
                date=workout.date
            )
            for workout in filtered_workouts
        ]


@workouts_router.get("/workouts/by-exercise", response_model=list[WorkoutResponse])
def get_all_workouts_for_exercise(exercise_id: str, current_user=Depends(get_current_user)):
    """Fetch all workouts for a specific exercise by the authenticated user"""
    with session_scope() as session:
        # Convert exercise_id to UUID
        try:
            exercise_uuid = str(UUID(exercise_id))  # Ensure it's a string UUID
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid exercise_id format")

        # Get user ID as a string
        db_user = session.query(User.id).filter_by(auth_id=current_user.id).scalar()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user_id = str(db_user)  # Convert user_id to string

        # Fetch all workouts, ordered by date (latest first)
        workouts = (
            session.query(Workout)
            .filter(Workout.user_id == db_user_id)
            .filter(cast(Workout.exercise_id, String) == exercise_id)
            .order_by(desc(Workout.date))
            .all()
        )

        # if not workouts:
        #     raise HTTPException(status_code=404, detail="No workouts found for this exercise")

        return [
            WorkoutResponse(
                id=workout.id,
                exercise_id=workout.exercise_id,
                reps=workout.reps,
                weights=workout.weights,
                date=workout.date
            )
            for workout in workouts
        ]


@workouts_router.post("/log-workout", status_code=201)
def log_workout(data: WorkoutCreate, current_user=Depends(get_current_user)):
    """Log a workout for the authenticated user"""
    with session_scope() as session:
        # ✅ Get authenticated user (fetching only necessary fields)
        db_user = session.query(User.id).filter_by(auth_id=current_user.id).scalar()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Check if exercise exists
        exercise_exists = session.query(Exercise.id).filter(Exercise.id == data.exercise_id).scalar()
        if not exercise_exists:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # ✅ Ensure `reps` and `weights` are the same length
        if len(data.reps) != len(data.weights):
            raise HTTPException(status_code=400, detail="Reps and weights lists must be the same length")

        # ✅ Log the workout
        new_workout = Workout(
            id=uuid4(),
            user_id=db_user,  # ✅ Using scalar result (UUID only, avoids detached instance error)
            exercise_id=data.exercise_id,
            reps=data.reps,
            weights=data.weights
        )
        session.add(new_workout)
        session.commit()

        return {"message": "Workout logged successfully", "workout_id": new_workout.id}

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
