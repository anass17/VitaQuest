from contextlib import asynccontextmanager
from fastapi import FastAPI
from utils.mlflow_evaluation import setup_mlflow
from db.base import Base
from db.session import engine
from routes.rag import router as rag_router
from routes.auth import router as auth_router
import db.models
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",  # dev on host
    "http://frontend:3000",  # frontend container
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP code

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

    setup_mlflow("vitaquest-rag-expirement")

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {"message": "API is running"}
