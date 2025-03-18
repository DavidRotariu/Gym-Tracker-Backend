from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routers.splits import get_current_user
from app.db.database import  session_scope
from app.db.models import Exercise
from app.db.models.user_favourite_exercise import UserFavoriteExercise

from app.db.models.users import User
from uuid import UUID, uuid4

favorites_router = APIRouter(tags=["Favorites"])

# ✅ Function to add an exercise to user's favorites
@favorites_router.post("/favorites/add", status_code=201)
def add_favorite(exercise_id: UUID, current_user=Depends(get_current_user)):
    """Fetch all splits for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        # ✅ Check if exercise exists
        db_exercise = session.query(Exercise).filter_by(id=exercise_id).first()
        if not db_exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        # ✅ Check if already favorited
        existing_fav = session.query(UserFavoriteExercise).filter_by(user_id=db_user.id, exercise_id=exercise_id).first()
        if existing_fav:
            raise HTTPException(status_code=400, detail="Exercise is already in favorites")

        # ✅ Add to favorites
        favorite = UserFavoriteExercise(id=uuid4(), user_id=db_user.id, exercise_id=exercise_id)
        session.add(favorite)

    return {"message": "Exercise added to favorites"}

# ✅ Function to remove an exercise from user's favorites
@favorites_router.delete("/favorites/remove", status_code=200)
def remove_favorite(exercise_id: UUID, current_user=Depends(get_current_user)):
    """Fetch all splits for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")


        # ✅ Check if favorite exists
        favorite = session.query(UserFavoriteExercise).filter_by(user_id=db_user.id, exercise_id=exercise_id).first()
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        # ✅ Remove favorite
        session.delete(favorite)

    return {"message": "Exercise removed from favorites"}

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
