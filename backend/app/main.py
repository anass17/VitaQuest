from fastapi import FastAPI, UploadFile, File
from services.rag_service import RAGService
from schemas.query import queryData
import json

app = FastAPI()

rag_service = RAGService()


EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_SIZE = 768
EMBEDDING_NORMALISE = True
CROSS_ENCODER = "BAAI/bge-reranker-large"
LLM_MODEL = "llama3:8b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 256



@app.get('/')
def hello():
    return {
        "message": "Hello !"
    }



@app.post("/document/ingest")
async def upload_pdf(
    file: UploadFile = File(...)
):

    chunks = rag_service.chunk_store_pipeline(file, EMBEDDING_MODEL, EMBEDDING_SIZE, EMBEDDING_NORMALISE)

    return {
        'Parent Chunks Count': len(chunks[0]),
        'Child Chunks Count': len(chunks[1])
    }



@app.post("/answer/generate")
async def upload_pdf(
    data: queryData
):

    answer = rag_service.retrieve_generate_pipeline(data.query, EMBEDDING_MODEL, CROSS_ENCODER, LLM_MODEL)

    return {
        "answer": answer
    }