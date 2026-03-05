from sqlalchemy.orm import Session

from app.db.models.users import User


class QRRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_auth_id(self, auth_id: str):
        return self.session.query(User).filter_by(auth_id=str(auth_id)).first()

    def save(self, user: User):
        self.session.add(user)
        self.session.commit()
