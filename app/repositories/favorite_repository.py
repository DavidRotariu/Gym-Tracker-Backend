from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models.user_favourite_exercise import UserFavoriteExercise


class FavoriteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user_and_exercise(self, user_id, exercise_id):
        return self.session.query(UserFavoriteExercise).filter_by(user_id=user_id, exercise_id=exercise_id).first()

    def list_for_user(self, user_id):
        return self.session.query(UserFavoriteExercise).filter_by(user_id=user_id).all()

    def create(self, user_id, exercise_id):
        favorite = UserFavoriteExercise(id=uuid4(), user_id=user_id, exercise_id=exercise_id)
        self.session.add(favorite)
        self.session.commit()
        self.session.refresh(favorite)
        return favorite

    def delete(self, favorite):
        self.session.delete(favorite)
        self.session.commit()
