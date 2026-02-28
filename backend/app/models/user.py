from db.models.user import User
from sqlalchemy.orm import Session


class UserModel:

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, first_name, last_name, email, hashed_password):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_email(self, email):
        user = self.db.query(User).filter(User.email == email).first()
        return user

    def get_user_by_id(self, id):
        user = self.db.query(User).filter(User.id == id).first()
        return user
