from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routers.splits import get_current_user
from app.api.schemas.exercises import ExerciseResponse
from app.db.database import  session_scope
from app.db.models import Exercise, Muscle
from app.db.models.user_favourite_exercise import UserFavoriteExercise

from app.db.models.users import User
from uuid import UUID, uuid4

favorites_router = APIRouter(tags=["Favorites"])

def fetch_exercises_by_muscle(session, muscle_id, user_id, exercise_id):
    """Fetch exercises for a muscle, ensuring favorite sorting"""
    muscle = session.query(Muscle).filter(Muscle.id == muscle_id).first()
    if not muscle:
        raise HTTPException(status_code=404, detail="Muscle not found")

    exercises = session.query(Exercise).filter(Exercise.muscle_id == muscle_id).all()

    favorite_exercise_ids = {
        fav.exercise_id for fav in session.query(UserFavoriteExercise).filter_by(user_id=user_id).all()
    }

    sorted_exercises = sorted(exercises, key=lambda x: x.id not in favorite_exercise_ids)

    return [
        ExerciseResponse(
            id=exercise.id,
            name=exercise.name,
            pic=f"/uploads/exercises/{exercise.pic}" if exercise.pic else None,
            tips=exercise.tips,
            equipment=exercise.equipment,
            favourite=(exercise.id in favorite_exercise_ids),
            primary_muscle=muscle.name,
            secondary_muscles=[
                session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                for sm in exercise.secondary_muscles
            ]
        ) for exercise in sorted_exercises
    ]


# ✅ Function to add an exercise to user's favorites
@favorites_router.post("/favorites/add", response_model=List[ExerciseResponse])
def add_favorite(exercise_id: UUID, current_user=Depends(get_current_user)):
    """Add an exercise to favorites and return updated exercises"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        db_exercise = session.query(Exercise).filter_by(id=exercise_id).first()
        if not db_exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        existing_fav = session.query(UserFavoriteExercise).filter_by(user_id=db_user.id, exercise_id=exercise_id).first()
        if existing_fav:
            raise HTTPException(status_code=400, detail="Exercise is already in favorites")

        favorite = UserFavoriteExercise(id=uuid4(), user_id=db_user.id, exercise_id=exercise_id)
        session.add(favorite)
        session.commit()
        session.refresh(favorite)

        # Fetch updated exercises for the primary muscle of this exercise
        return fetch_exercises_by_muscle(session, db_exercise.muscle_id, db_user.id, exercise_id)


# ✅ Function to remove an exercise from user's favorites
@favorites_router.delete("/favorites/remove", response_model=List[ExerciseResponse])
def remove_favorite(exercise_id: UUID, current_user=Depends(get_current_user)):
    """Remove an exercise from favorites and return updated exercises"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        favorite = session.query(UserFavoriteExercise).filter_by(user_id=db_user.id, exercise_id=exercise_id).first()
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        session.delete(favorite)
        session.commit()

        # Fetch updated exercises for the primary muscle of this exercise
        db_exercise = session.query(Exercise).filter_by(id=exercise_id).first()
        return fetch_exercises_by_muscle(session, db_exercise.muscle_id, db_user.id, exercise_id)


# ✅ Function to get all favorite exercises for a user
@favorites_router.get("/favorites", status_code=200)
def get_favorites(current_user=Depends(get_current_user)):
    """Fetch all splits for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        # ✅ Get user's favorite exercises
        favorites = session.query(UserFavoriteExercise).filter_by(user_id=db_user.id).all()
        return {"favorite_exercises": [fav.exercise_id for fav in favorites]}
