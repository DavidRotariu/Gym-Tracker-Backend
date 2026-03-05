from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models.users import User


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_auth_id(self, auth_id: str):
        return self.session.query(User).filter_by(auth_id=str(auth_id)).first()

    def create_user(self, auth_id: str, email: str, name: str):
        user = User(id=uuid4(), auth_id=str(auth_id), email=email, name=name)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
