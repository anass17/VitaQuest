from fastapi import APIRouter, Depends, HTTPException, status
from services.auth_service import AuthService
from db.deps import get_db
from sqlalchemy.orm import Session
from schemas.auth import AuthResponse, RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


# Register Endpoint


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    controller = AuthService(db)
    token = controller.register_user(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    return token


# Login Endpoint


@router.post("/login", response_model=AuthResponse)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    controller = AuthService(db)
    token = controller.authenticate_user(
        email=form_data.email, password=form_data.password
    )

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return token
