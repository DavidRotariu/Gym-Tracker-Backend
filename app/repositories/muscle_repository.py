from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models.muscles import Muscle


class MuscleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Muscle]:
        return self.session.query(Muscle).all()

    def get_by_id(self, muscle_id):
        return self.session.query(Muscle).filter_by(id=muscle_id).first()

    def get_name_by_id(self, muscle_id):
        return self.session.query(Muscle.name).filter(Muscle.id == muscle_id).scalar()

    def get_by_name(self, name: str):
        return self.session.query(Muscle).filter_by(name=name).first()

    def create(self, name: str, pic: str | None):
        muscle = Muscle(id=uuid4(), name=name, pic=pic)
        self.session.add(muscle)
        self.session.commit()
        self.session.refresh(muscle)
        return muscle
