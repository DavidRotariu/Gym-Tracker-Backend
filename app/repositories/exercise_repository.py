from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models.exercises import Exercise
from app.db.models.exercise_secondary_muscles import ExerciseSecondaryMuscle


class ExerciseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Exercise]:
        return self.session.query(Exercise).all()

    def get_by_id(self, exercise_id):
        return self.session.query(Exercise).filter_by(id=exercise_id).first()

    def get_by_name(self, name: str):
        return self.session.query(Exercise).filter_by(name=name).first()

    def list_by_primary_muscle(self, muscle_id):
        return self.session.query(Exercise).filter(Exercise.muscle_id == muscle_id).all()

    def create(self, data):
        exercise = Exercise(
            id=uuid4(),
            name=data.name,
            pic=data.pic,
            tips=data.tips,
            equipment=data.equipment,
            favourite=data.favourite,
            muscle_id=data.muscle_id,
        )
        self.session.add(exercise)
        self.session.flush()
        return exercise

    def add_secondary_muscle(self, exercise_id, muscle_id):
        self.session.add(ExerciseSecondaryMuscle(exercise_id=exercise_id, muscle_id=muscle_id))

    def list_secondary_links(self, exercise_id):
        return (
            self.session.query(ExerciseSecondaryMuscle)
            .filter(ExerciseSecondaryMuscle.exercise_id == exercise_id)
            .all()
        )
