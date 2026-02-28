from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, func
from db.base import Base
from db.enums.role_enum import EnumRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(EnumRole, name="role_enum"), nullable=False, default="USER")
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
