from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy import func

from app.core.supabase import supabase_client
from app.db.database import session_scope
from app.db.models import Muscle, SplitMuscle, User, Workout, Exercise
from app.db.models.splits import Split
from app.api.schemas.splits import SplitCreate, SplitResponse, MuscleResponse, SplitMuscleCreate, SplitMuscleResponse, \
    SplitMuscleResponse2, SplitResponse2
from uuid import uuid4, UUID
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

        # Get all splits for the user
        splits = session.query(Split).filter(Split.user_id == db_user.id).all()

        # Calculate today's start time in UTC
        now_utc = datetime.now(timezone.utc)
        today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get exercise counts by muscle for today's workouts for THIS user
        exercise_counts = {}
        today_workouts = (session.query(Exercise.muscle_id, func.count(Workout.id).label('count'))
                          .join(Workout, Workout.exercise_id == Exercise.id)
                          .filter(Workout.user_id == db_user.id)  # Filter by the current user
                          .filter(Workout.date >= today_start)
                          .group_by(Exercise.muscle_id)
                          .all())

        for muscle_id, count in today_workouts:
            exercise_counts[muscle_id] = count

        result = []

        for split in splits:
            # Get top 3 muscles for this split for the description
            top_muscles = (session.query(Muscle)
                           .join(SplitMuscle, Muscle.id == SplitMuscle.muscle_id)
                           .filter(SplitMuscle.split_id == split.id)
                           .order_by(SplitMuscle.nr_of_exercises.desc())
                           .limit(3)
                           .all())

            description = " / ".join([muscle.name for muscle in top_muscles])

            # Get all muscles for this split in a single query
            split_muscles = (session.query(SplitMuscle, Muscle)
                             .join(Muscle, SplitMuscle.muscle_id == Muscle.id)
                             .filter(SplitMuscle.split_id == split.id)
                             .all())

            muscles_data = []
            for sm, muscle in split_muscles:
                muscles_data.append(
                    SplitMuscleResponse(
                        id=muscle.id,
                        name=muscle.name,
                        pic=f"/uploads/muscles/{muscle.pic}" if muscle.pic else None,
                        nr_of_exercises=sm.nr_of_exercises,
                        nr_of_exercises_done_today=exercise_counts.get(muscle.id, 0)
                    )
                )

            result.append(
                SplitResponse(
                    id=split.id,
                    name=split.name,
                    pic=split.pic,
                    description=description,
                    muscles=muscles_data
                )
            )

        return result

@splits_router.post("/splits", response_model=SplitResponse2, status_code=201)
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
                SplitMuscleResponse2(
                    id=muscle.id,
                    name=muscle.name,
                    pic=muscle.pic,
                    nr_of_exercises=muscle_data.nr_of_exercises
                )
            )

        session.commit()  # ✅ Finalizes changes

        return SplitResponse2(
            id=new_split.id,
            name=new_split.name,
            pic=new_split.pic,
            description=" / ".join([m.name for m in return_muscles]),  # ✅ Construct description
            muscles=return_muscles  # ✅ Return full muscle details
        )


@splits_router.delete("/splits/{split_id}", status_code=204)
def delete_split(split_id: UUID, current_user=Depends(get_current_user)):
    """Delete a workout split for an authenticated user"""
    with session_scope() as session:
        db_user = session.query(User).filter_by(auth_id=current_user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found in database")

        split = session.query(Split).filter(Split.id == split_id, Split.user_id == db_user.id).first()
        if not split:
            raise HTTPException(status_code=404, detail="Split not found or unauthorized access")

        # Delete related SplitMuscle entries first
        session.query(SplitMuscle).filter(SplitMuscle.split_id == split_id).delete()

        # Delete the split itself
        session.delete(split)

        return {"message": "Split deleted successfully"}
