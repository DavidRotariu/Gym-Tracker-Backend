from typing import List
from uuid import uuid4, UUID
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import session_scope
from app.db.models import Muscle
from app.db.models.exercises import Exercise
from app.db.models.exercise_secondary_muscles import ExerciseSecondaryMuscle
from app.api.schemas.exercises import ExerciseCreate, ExerciseResponse, ExerciseBulkCreate

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
                pic=f"/uploads/exercises/{exercise.pic}" if exercise.pic else None,
                tips=exercise.tips,
                equipment=exercise.equipment,
                favourite=exercise.favourite,
                primary_muscle=session.query(Muscle.name).filter(Muscle.id == exercise.muscle_id).scalar(),
                secondary_muscles=[
                    session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                    for sm in session.query(ExerciseSecondaryMuscle).filter(
                        ExerciseSecondaryMuscle.exercise_id == exercise.id).all()
                ]
            ) for exercise in exercises
        ]


@exercises_router.get("/exercises/by-muscle/{muscle_id}", response_model=List[ExerciseResponse])
def get_exercises_by_primary_muscle(muscle_id: UUID):
    """Fetch all exercises where the given muscle is the primary muscle"""
    with session_scope() as session:
        # ✅ Check if muscle exists
        muscle = session.query(Muscle).filter(Muscle.id == muscle_id).first()
        if not muscle:
            raise HTTPException(status_code=404, detail="Muscle not found")

        # ✅ Fetch exercises with this muscle as primary
        exercises = session.query(Exercise).filter(Exercise.muscle_id == muscle_id).all()

        return [
            ExerciseResponse(
                id=exercise.id,
                name=exercise.name,
                pic=f"/uploads/exercises/{exercise.pic}" if exercise.pic else None,
                tips=exercise.tips,
                equipment=exercise.equipment,
                favourite=exercise.favourite,
                primary_muscle=muscle.name,  # ✅ Return primary muscle name
                secondary_muscles=[
                    session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                    for sm in exercise.secondary_muscles
                ]
            ) for exercise in exercises
        ]


@exercises_router.post("/exercises", response_model=ExerciseResponse, status_code=201)
def create_exercise(data: ExerciseCreate):
    """Create a new exercise"""
    with session_scope() as session:
        # ✅ Check if primary muscle exists
        primary_muscle = session.query(Muscle).filter_by(id=data.muscle_id).first()
        if not primary_muscle:
            raise HTTPException(status_code=400, detail="Primary muscle not found")

        # ✅ Check if exercise already exists
        existing_exercise = session.query(Exercise).filter_by(name=data.name).first()
        if existing_exercise:
            raise HTTPException(status_code=400, detail="Exercise already exists")

        # ✅ Create new exercise
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
        session.flush()  # ✅ Ensures `new_exercise.id` is available before inserting secondary muscles

        # ✅ Insert secondary muscles
        for muscle_id in data.secondary_muscles:
            secondary_muscle = session.query(Muscle).filter_by(id=muscle_id).first()
            if not secondary_muscle:
                raise HTTPException(status_code=400, detail=f"Secondary muscle with ID {muscle_id} not found")

            session.add(ExerciseSecondaryMuscle(exercise_id=new_exercise.id, muscle_id=muscle_id))

        session.commit()

        return ExerciseResponse(
            id=new_exercise.id,
            name=new_exercise.name,
            pic=new_exercise.pic,
            tips=new_exercise.tips,
            equipment=new_exercise.equipment,
            favourite=new_exercise.favourite,
            primary_muscle=primary_muscle.name,
            secondary_muscles=[
                session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                for sm in session.query(ExerciseSecondaryMuscle).filter(
                    ExerciseSecondaryMuscle.exercise_id == new_exercise.id).all()
            ]
        )


@exercises_router.post("/exercises/bulk", response_model=List[ExerciseResponse], status_code=201)
def create_exercises_bulk(data: ExerciseBulkCreate):
    """Create multiple exercises at once"""
    with session_scope() as session:
        created_exercises = []

        for exercise_data in data.exercises:
            # ✅ Check if primary muscle exists
            primary_muscle = session.query(Muscle).filter_by(id=exercise_data.muscle_id).first()
            if not primary_muscle:
                raise HTTPException(status_code=400, detail=f"Primary muscle {exercise_data.muscle_id} not found")

            # ✅ Check if exercise already exists
            existing_exercise = session.query(Exercise).filter_by(name=exercise_data.name).first()
            if existing_exercise:
                continue  # Skip duplicate exercises

            # ✅ Create new exercise
            new_exercise = Exercise(
                id=uuid4(),
                name=exercise_data.name,
                pic=exercise_data.pic,
                tips=exercise_data.tips,
                equipment=exercise_data.equipment,
                favourite=exercise_data.favourite,
                muscle_id=exercise_data.muscle_id
            )
            session.add(new_exercise)
            session.flush()  # ✅ Ensures `new_exercise.id` is available before inserting secondary muscles

            # ✅ Insert secondary muscles
            for muscle_id in exercise_data.secondary_muscles:
                secondary_muscle = session.query(Muscle).filter_by(id=muscle_id).first()
                if not secondary_muscle:
                    raise HTTPException(status_code=400, detail=f"Secondary muscle {muscle_id} not found")

                session.add(ExerciseSecondaryMuscle(exercise_id=new_exercise.id, muscle_id=muscle_id))

            created_exercises.append(
                ExerciseResponse(
                    id=new_exercise.id,
                    name=new_exercise.name,
                    pic=new_exercise.pic,
                    tips=new_exercise.tips,
                    equipment=new_exercise.equipment,
                    favourite=new_exercise.favourite,
                    primary_muscle=primary_muscle.name,
                    secondary_muscles=[
                        session.query(Muscle.name).filter(Muscle.id == sm.muscle_id).scalar()
                        for sm in session.query(ExerciseSecondaryMuscle).filter(
                            ExerciseSecondaryMuscle.exercise_id == new_exercise.id).all()
                    ]
                )
            )

        session.commit()

        return created_exercises  # ✅ Return all successfully created exercises
