from core.security import create_access_token, verify_password, hash_password
from models.user import UserModel


class AuthService:

    def __init__(self, db):
        self.db = db
        self.model = UserModel(db)

    def register_user(self, first_name: str, last_name: str, email: str, password: str):
        existing_user = self.model.get_user_by_email(email)

        first_name = first_name.capitalize()
        last_name = last_name.capitalize()

        if existing_user:
            return None

        user = self.model.create_user(
            first_name, last_name, email, hash_password(password)
        )

        token = create_access_token({"sub": str(user.id), "role": user.role})

        return {
            "access_token": token,
            "first_name": first_name,
            "last_name": last_name,
            "role": "USER",
        }

    def authenticate_user(self, email: str, password: str):
        user = self.model.get_user_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        token = create_access_token({"sub": str(user.id), "role": user.role})
        return {
            "access_token": token,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
